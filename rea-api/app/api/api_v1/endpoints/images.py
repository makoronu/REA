"""
物件画像API

画像のアップロード・削除・更新を行う。
メタデータはproperty_imagesテーブルで管理。
"""
import os
import uuid
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from shared.auth.middleware import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

# アップロード先ディレクトリ
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'uploads', 'properties')

# 許可する画像形式
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def require_auth(request: Request) -> dict:
    """認証を要求（ログイン必須）"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="認証が必要です")
    return user


def get_file_extension(filename: str) -> str:
    """ファイル拡張子を取得"""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


def validate_image_file(file: UploadFile) -> None:
    """画像ファイルのバリデーション"""
    ext = get_file_extension(file.filename or '')
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"許可されていないファイル形式です。許可: {', '.join(ALLOWED_EXTENSIONS)}"
        )


@router.get("/{property_id}/images")
def get_property_images(
    request: Request,
    property_id: int,
    db: Session = Depends(get_db),
):
    """物件の画像一覧を取得"""
    require_auth(request)

    result = db.execute(
        text("""
            SELECT id, property_id, image_type, file_path, file_url,
                   display_order, caption, is_public,
                   created_at, updated_at
            FROM property_images
            WHERE property_id = :property_id
              AND deleted_at IS NULL
            ORDER BY display_order, id
        """),
        {"property_id": property_id}
    )

    images = []
    for row in result:
        images.append({
            "id": row.id,
            "property_id": row.property_id,
            "image_type": row.image_type,
            "file_path": row.file_path,
            "file_url": row.file_url,
            "display_order": row.display_order,
            "caption": row.caption,
            "is_public": row.is_public,
        })

    return images


@router.post("/{property_id}/images")
async def upload_property_image(
    request: Request,
    property_id: int,
    file: UploadFile = File(...),
    image_type: str = Form(default="0"),
    display_order: int = Form(default=1),
    caption: str = Form(default=""),
    is_public: bool = Form(default=True),
    db: Session = Depends(get_db),
):
    """物件画像をアップロード"""
    require_auth(request)

    # バリデーション
    validate_image_file(file)

    # ファイルサイズチェック
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="ファイルサイズが10MBを超えています")

    # アップロードディレクトリ作成
    property_dir = os.path.join(UPLOAD_DIR, str(property_id))
    os.makedirs(property_dir, exist_ok=True)

    # ユニークなファイル名を生成
    ext = get_file_extension(file.filename or 'jpg')
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(property_dir, unique_filename)

    # ファイル保存
    try:
        with open(file_path, 'wb') as f:
            f.write(contents)
    except IOError as e:
        logger.error(f"Failed to save image: {e}")
        raise HTTPException(status_code=500, detail="画像の保存に失敗しました")

    # 相対パス（DB保存用）
    relative_path = f"properties/{property_id}/{unique_filename}"
    file_url = f"/uploads/{relative_path}"

    # DBに保存
    try:
        result = db.execute(
            text("""
                INSERT INTO property_images
                (property_id, image_type, file_path, file_url, display_order, caption, is_public)
                VALUES (:property_id, :image_type, :file_path, :file_url, :display_order, :caption, :is_public)
                RETURNING id, property_id, image_type, file_path, file_url, display_order, caption, is_public
            """),
            {
                "property_id": property_id,
                "image_type": image_type,
                "file_path": relative_path,
                "file_url": file_url,
                "display_order": display_order,
                "caption": caption,
                "is_public": is_public,
            }
        )
        db.commit()

        row = result.fetchone()
        return {
            "id": row.id,
            "property_id": row.property_id,
            "image_type": row.image_type,
            "file_path": row.file_path,
            "file_url": row.file_url,
            "display_order": row.display_order,
            "caption": row.caption,
            "is_public": row.is_public,
        }
    except Exception as e:
        db.rollback()
        # ファイルも削除
        if os.path.exists(file_path):
            os.remove(file_path)
        logger.error(f"Failed to save image record: {e}")
        raise HTTPException(status_code=500, detail=f"画像の登録に失敗しました: {str(e)}")


@router.put("/{property_id}/images/{image_id}")
def update_property_image(
    request: Request,
    property_id: int,
    image_id: int,
    data: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """物件画像のメタデータを更新"""
    require_auth(request)

    # 存在確認
    existing = db.execute(
        text("""
            SELECT id FROM property_images
            WHERE id = :image_id AND property_id = :property_id AND deleted_at IS NULL
        """),
        {"image_id": image_id, "property_id": property_id}
    ).fetchone()

    if not existing:
        raise HTTPException(status_code=404, detail="画像が見つかりません")

    # 更新可能なフィールドのみ抽出
    allowed_fields = {'image_type', 'display_order', 'caption', 'is_public'}
    update_data = {k: v for k, v in data.items() if k in allowed_fields}

    if not update_data:
        return {"message": "更新するデータがありません"}

    # SET句を構築
    set_parts = [f"{k} = :{k}" for k in update_data.keys()]
    set_clause = ", ".join(set_parts)
    update_data["image_id"] = image_id

    try:
        db.execute(
            text(f"""
                UPDATE property_images
                SET {set_clause}, updated_at = NOW()
                WHERE id = :image_id
            """),
            update_data
        )
        db.commit()

        # 更新後のデータを返す
        result = db.execute(
            text("""
                SELECT id, property_id, image_type, file_path, file_url,
                       display_order, caption, is_public
                FROM property_images
                WHERE id = :image_id AND deleted_at IS NULL
            """),
            {"image_id": image_id}
        ).fetchone()

        return {
            "id": result.id,
            "property_id": result.property_id,
            "image_type": result.image_type,
            "file_path": result.file_path,
            "file_url": result.file_url,
            "display_order": result.display_order,
            "caption": result.caption,
            "is_public": result.is_public,
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update image: {e}")
        raise HTTPException(status_code=500, detail=f"画像の更新に失敗しました: {str(e)}")


@router.delete("/{property_id}/images/{image_id}")
def delete_property_image(
    request: Request,
    property_id: int,
    image_id: int,
    db: Session = Depends(get_db),
):
    """物件画像を論理削除"""
    require_auth(request)

    # 存在確認
    existing = db.execute(
        text("""
            SELECT id, file_path FROM property_images
            WHERE id = :image_id AND property_id = :property_id AND deleted_at IS NULL
        """),
        {"image_id": image_id, "property_id": property_id}
    ).fetchone()

    if not existing:
        raise HTTPException(status_code=404, detail="画像が見つかりません")

    try:
        # 論理削除
        db.execute(
            text("""
                UPDATE property_images
                SET deleted_at = NOW()
                WHERE id = :image_id
            """),
            {"image_id": image_id}
        )
        db.commit()

        return {"message": "画像を削除しました", "id": image_id}
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete image: {e}")
        raise HTTPException(status_code=500, detail=f"画像の削除に失敗しました: {str(e)}")


@router.post("/{property_id}/images/bulk")
async def bulk_update_images(
    request: Request,
    property_id: int,
    images: List[Dict[str, Any]],
    db: Session = Depends(get_db),
):
    """
    物件画像の一括更新（メタデータのみ）
    新規画像はPOST /{property_id}/imagesで個別にアップロード後、
    このエンドポイントでメタデータを一括更新する。
    """
    require_auth(request)

    results = []

    for img_data in images:
        image_id = img_data.get('id')
        if not image_id:
            continue

        # 更新可能フィールドのみ
        allowed_fields = {'image_type', 'display_order', 'caption', 'is_public'}
        update_data = {k: v for k, v in img_data.items() if k in allowed_fields}

        if not update_data:
            continue

        set_parts = [f"{k} = :{k}" for k in update_data.keys()]
        set_clause = ", ".join(set_parts)
        update_data["image_id"] = image_id
        update_data["property_id"] = property_id

        try:
            db.execute(
                text(f"""
                    UPDATE property_images
                    SET {set_clause}, updated_at = NOW()
                    WHERE id = :image_id AND property_id = :property_id AND deleted_at IS NULL
                """),
                update_data
            )
            results.append({"id": image_id, "status": "updated"})
        except Exception as e:
            logger.warning(f"Failed to update image {image_id}: {e}")
            results.append({"id": image_id, "status": "error", "message": str(e)})

    db.commit()

    return {"updated": len([r for r in results if r["status"] == "updated"]), "results": results}

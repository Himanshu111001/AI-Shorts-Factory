import uuid
from typing import Sequence, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.models.generated_image import GeneratedImage

class GeneratedImageRepository:
    """
    Repository for managing GeneratedImage entities in the database.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, image_data: dict) -> GeneratedImage:
        image = GeneratedImage(**image_data)
        self.db.add(image)
        try:
            self.db.commit()
            self.db.refresh(image)
            return image
        except Exception:
            self.db.rollback()
            raise

    def create_many(self, images_data: list[dict]) -> list[GeneratedImage]:
        images = [GeneratedImage(**data) for data in images_data]
        self.db.add_all(images)
        try:
            self.db.commit()
            for img in images:
                self.db.refresh(img)
            return images
        except Exception:
            self.db.rollback()
            raise

    def get_by_id(self, image_id: uuid.UUID) -> Optional[GeneratedImage]:
        stmt = select(GeneratedImage).where(GeneratedImage.id == image_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_video_id(self, video_id: uuid.UUID) -> Sequence[GeneratedImage]:
        stmt = select(GeneratedImage).where(GeneratedImage.video_id == video_id).order_by(GeneratedImage.sequence_index.asc())
        return self.db.execute(stmt).scalars().all()

    def delete(self, image_id: uuid.UUID) -> bool:
        image = self.get_by_id(image_id)
        if not image:
            raise ValueError(f"GeneratedImage with id {image_id} not found.")
        self.db.delete(image)
        self.db.commit()
        return True

    def delete_by_video_id(self, video_id: uuid.UUID) -> int:
        images = self.get_by_video_id(video_id)
        count = len(images)
        for img in images:
            self.db.delete(img)
        self.db.commit()
        return count

    def replace_for_video(self, video_id: uuid.UUID, images_data: list[dict]) -> list[GeneratedImage]:
        """
        Atomically replaces all GeneratedImage rows for a specific video.
        """
        # Delete existing
        existing_images = self.get_by_video_id(video_id)
        for img in existing_images:
            self.db.delete(img)
        
        self.db.flush()
            
        # Insert new
        new_images = [GeneratedImage(**data) for data in images_data]
        self.db.add_all(new_images)
        
        try:
            self.db.commit()
            for img in new_images:
                self.db.refresh(img)
            return new_images
        except Exception:
            self.db.rollback()
            raise

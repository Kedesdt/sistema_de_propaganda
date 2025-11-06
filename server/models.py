from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Video(db.Model):
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    radius_km = db.Column(db.Float, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Video {self.filename}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'radius_km': self.radius_km,
            'uploaded_at': self.uploaded_at.isoformat()
        }

class SystemStatus(db.Model):
    __tablename__ = 'system_status'
    
    id = db.Column(db.Integer, primary_key=True)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def get_last_update():
        status = SystemStatus.query.first()
        if not status:
            status = SystemStatus()
            db.session.add(status)
            db.session.commit()
        return status.last_update
    
    @staticmethod
    def update_timestamp():
        status = SystemStatus.query.first()
        if not status:
            status = SystemStatus()
            db.session.add(status)
        status.last_update = datetime.utcnow()
        db.session.commit()
        return status.last_update

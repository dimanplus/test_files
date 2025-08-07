'''
файл test_db.db

CREATE TABLE "files" (
	"file_name"	TEXT NOT NULL UNIQUE,
	"download"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("file_name")
)
'''

from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class File(Base):
    __tablename__ = "files"
    file_name: Mapped[str] = mapped_column(String, primary_key=True)
    download: Mapped[int] = mapped_column(Integer, default=0)
    def __repr__(self):
        return f"File(file_name={self.file_name!r}, download={self.download})"
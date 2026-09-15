from database import engine
from models import Base
from migrate import migrate

print("Создаем таблицы в базе данных...")
Base.metadata.create_all(bind=engine)
migrate()
print("Таблицы созданы!")

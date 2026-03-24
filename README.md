To run the application localy:      py -m uvicorn main:app --reload

To run the application on docker:   docker-compose up --build
To run the application BE: docker-compose build euro_stat_be
To delete Images:  docker-compose down --remove-orphans

MongoDB:
Authentication: User & password
User : admin
Password : admin123
Data base: euro_stat_db
URL: mongodb://localhost:27017/euro_stat_db?authSource=admin
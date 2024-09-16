from sqlalchemy import create_engine, Column, Integer, String, Sequence, MetaData, text
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

class Posts(Base):
    __tablename__ = "posts"
    id = Column(Integer, Sequence("posts_id_seq"), primary_key=True)
    title = Column(String())
    body = Column(String())
    upvote = Column(Integer)
    views = Column(Integer)
    location = Column(String())

    def __repr__(self):
        return f"<Posts(title='{self.title}', body='{self.body}', upvote={self.upvote}, views={self.views}, location='{self.location}')>"

class AppUser(Base):
    __tablename__ = "app_user"
    id = Column(Integer, Sequence("app_user_id_seq"), primary_key=True)
    username = Column(String())
    location = Column(String())

    def __repr__(self):
        return f"<AppUser(username='{self.username}', location='{self.location}')>"

class Petitions(Base):
    __tablename__ = "petitions"
    id = Column(Integer, Sequence("petitions_id_seq"), primary_key=True)
    alternate_id = Column(Integer())
    title = Column(String())
    body = Column(String())
    location = Column(String())
    date = Column(Integer())

    def __repr__(self):
        return f"<Petitions(title='{self.title}', body='{self.body}', location='{self.location}', date={self.date})>"

class Signatures(Base):
    __tablename__ = "signatures"
    id = Column(Integer, Sequence("signatures_id_seq"), primary_key=True)
    petition_id = Column(Integer())
    username = Column(String())
    
    def __repr__(self):
        return f"<Signatures(petition_id={self.petition_id}, username='{self.username}')>"
    

class DbActions:
    def __init__(self, db_url:str) -> None:
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def append(self, values: list, debug=False) -> None:
        session = self.Session()
        try:
            if len(values) == 5 and isinstance(values[0], str) and isinstance(values[1], str) and isinstance(values[2], int) and isinstance(values[3], int) and isinstance(values[4], str):
                db_value = Posts(title=values[0], body=values[1], upvote=values[2], views=values[3], location=values[4])
                session.add(db_value)
            elif len(values) == 2 and isinstance(values[0], str) and isinstance(values[1], str):
                db_value = AppUser(username=values[0], location=values[1])
                session.add(db_value)
            elif len(values) == 5 and isinstance(values[0], str) and isinstance(values[1], int) and isinstance(values[2], str) and isinstance(values[3], str) and isinstance(values[4], int):
                db_value = Petitions(title=values[0], alternate_id=values[1], body=values[2], location=values[3], date=values[4])
                session.add(db_value)
            elif len(values) == 2 and isinstance(values[0], int) and isinstance(values[1], str):
                db_value = Signatures(petition_id=values[0], username=values[1])
                session.add(db_value)
            
            else:
                print(len(values) == 5, isinstance(values[0], str) , isinstance(values[1], int) , isinstance(values[2], str) , isinstance(values[3], str) , isinstance(values[4], int))
                raise ValueError(f"Invalid values")
            
            session.commit()
            if debug:
                print("Values have been appended.")
        except Exception as e:
            session.rollback()
            print(f"Error in append: {e}")
        finally:
            session.close()


    def read(self, table: str, column: str, column_value: str, debug=False) -> list:
        with self.engine.connect() as connection:
            query = text(f"SELECT * FROM {table} WHERE {column} = :value")
            if debug:
                print(f"Executing query: {query} with value: {column_value}")
            result = connection.execute(query, {"value": column_value})
            rows = result.fetchall()
            if debug:
                for row in rows:
                    print(row)
            return rows

    def view_post(self,  debug=False) -> list:
        with self.engine.connect() as connection:
            query = text(f"SELECT * FROM posts ORDER BY views DESC LIMIT 3;")
            result = connection.execute(query)
            rows = result.fetchall()
            if debug:
                for row in rows:
                    print(row)
                    
            return rows
    
    def increment_post(self, post_id: int, debug=False) -> None:
        with self.engine.connect() as connection:
            with connection.begin():
                query = text("UPDATE posts SET views = views + 1 WHERE id = :id")
                if debug:
                    print(f"Executing query: {query} with value: {post_id}")
                connection.execute(query, {"id": post_id})
                if debug:
                    print(f"Post {post_id} has been incremented.")
                        
                    
    def read_table(self, table: str, debug=False) -> list[String]:
        with self.engine.connect() as connection:
            result = connection.execute(text(f"SELECT * FROM {table}"))
            rows = result.fetchall()
            if debug:
                for row in rows:
                    print(row)
            return rows

    def wipe_except_posts(self) -> None:
        metadata = MetaData()
        metadata.reflect(bind=self.engine)
        tables_to_drop = [table for table in metadata.sorted_tables if table.name != 'posts']
 

    def wipe(self) -> None:
        metadata = MetaData()
        metadata.reflect(bind=self.engine)
        metadata.drop_all(bind=self.engine)
        print("All tables have been dropped.")

    def cmd(self, command: str) -> None:
        with self.engine.connect() as connection:
            connection.execute(text(command))
    
if __name__ == "__main__":
    db = DbActions("postgresql://serentiy2_user:Kr2Y2KBIRn2nOY9hBEHOLIOKo1atVpKO@dpg-crir5ulumphs73cpejc0-a.ohio-postgres.render.com/serentiy2")
    
    db.view_post(debug=True)
    
    #db.read_table("posts", debug=True)
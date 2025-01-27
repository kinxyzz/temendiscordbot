from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import desc
from models import UserScore

class UserScoreRepository:
    def __init__(self, session: Session):
        self.session = session

    def insert_or_update_user_scores(self, user_score_data):
        """
        Memasukkan atau memperbarui data skor pengguna dalam database.
        
        :param user_score_data: List of dictionaries, masing-masing berisi data skor pengguna.
        """
        stmt_user_score = insert(UserScore).values(user_score_data)
        stmt_user_score = stmt_user_score.on_conflict_do_update(
            index_elements=["userId"],
            set_={"score": UserScore.score + 10}
        )
        self.session.execute(stmt_user_score)
        self.session.commit()

    def get_top_ten(self):
        """
        Mengambil 10 pengguna dengan skor tertinggi.
        
        :return: List of UserScore objects.
        """
        return (
            self.session.query(UserScore)
            .order_by(desc(UserScore.score))
            .limit(10)
            .all()
        )
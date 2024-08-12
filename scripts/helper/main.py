from pathlib import Path
import sys


sys.path.append(str(Path(__file__).parent.parent.parent))
from src.database import SessionMaker
from src.models.collectable import Collectable, CollectableMapInfo


if __name__ == "__main__":
    session = SessionMaker()
    temp1 = session.query(CollectableMapInfo).first()
    print(temp1)
    temp = session.query(Collectable).first()
    print(temp)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import Base, Category,Item, User

engine = create_engine('postgresql://catalog:catalog@localhost/catalog')

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# BODY

category1 = Category(name ="Fantasy")
session.add(category1)
session.commit()

category2 = Category(name ="Sci-Fi")
session.add(category2)
session.commit()

category3 = Category(name ="Horror")
session.add(category3)
session.commit()

category4 = Category(name ="History")
session.add(category4)
session.commit()


category5 = Category(name ="Philosophy")
session.add(category5)
session.commit()

category6 = Category(name ="Cookbooks")
session.add(category6)
session.commit()

category7 = Category(name ="Detective Novel")
session.add(category7)
session.commit()


category8 = Category(name ="Autobiography")
session.add(category8)
session.commit()

category9 = Category(name ="Romance")
session.add(category9)
session.commit()

# END BODY


print "added books!"

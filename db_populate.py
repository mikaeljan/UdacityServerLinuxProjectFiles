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
User1 = User(name="Geralt of Rivia",
             email="GeraltGrey@temeria.com")
session.add(User1)
session.commit()

category1 = Category(name ="Fantasy")
session.add(category1)
session.commit()

item1 = Item(creator_id=1,author ="J.R.R. Tolkien", book_title="Lord of The Rings, The Fellowship of the Ring", description="Story about a hobbit who ventures to save the Middle-Earth",
                     price="$4.99",year_published = 1954 ,category=category1)
session.add(item1)
session.commit()
item2 = Item(creator_id=1,author='G.R.R. Martin',book_title="The Game of Thrones-Feast for Crows", description="Story about a power-struggle who will win the Iron Throne and rule the Seven Kingdoms",
                     price="$14.99", year_published = 2005,category=category1)
session.add(item2)
session.commit()
category2 = Category(name ="Sci-Fi")
session.add(category2)
session.commit()

category3 = Category(name ="Horror")
session.add(category3)
session.commit()

item4 = Item(creator_id=1,author="Bram Stoker",book_title="Dracula",description="The novel tells the story of Dracula's attempt to move from Transylvania to England so that he may find new blood and spread the undead curse, and of the battle between Dracula and a small group of men and women led by Professor Abraham Van Helsing.",
                     price="$8.99",year_published=1966,category=category3)
session.add(item4)
session.commit()

category4 = Category(name ="History")
session.add(category4)
session.commit()

item5 = Item(creator_id=1,author="Robert Tombs",book_title="The English and their History",description="The history from a weird point of view.",
                     price="$14.99",year_published=2014,category=category4)
session.add(item5)
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

item8 = Item(creator_id=1,author="Sir Arthur Conan Doyle",book_title="The Adventures of Sherlock Holmes",description="The Adventures of Sherlock Holmes is a collection of twelve short stories by Arthur Conan Doyle, featuring his fictional detective Sherlock Holmes.",
                     price="$8.99",year_published=1892,category=category7)
session.add(item8)
session.commit()

category8 = Category(name ="Autobiography")
session.add(category8)
session.commit()

item9= Item(creator_id=1,author="Nelson Mandela",book_title="Long Walk to Freedom",description="Long Walk to Freedom is an autobiographical work written by South African President Nelson Mandela, and first published in 1994 by Little Brown & Co.",
                     price="$11.99",year_published=1994,category=category8)

session.add(item9)
session.commit()

category9 = Category(name ="Romance")
session.add(category9)
session.commit()

item9 = Item(creator_id=1,author="Jane Austen",book_title="Pride and Prejudice",description="Pride and Prejudice is a novel by Jane Austen, first published in 1813. The story charts the emotional development of the protagonist, Elizabeth Bennet, who learns the error of making hasty judgements and comes to appreciate the difference between the superficial and the essential.",
                     price="$0.99",year_published=1813,category=category9)
session.add(item9)
session.commit()
# END BODY


print "added books!"

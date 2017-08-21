from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Books, User, User_Books

engine = create_engine('sqlite:///littleelibrary.db')
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


# Create a couple dummy users
User1 = User(name="Jon Murphy", email="jmurphy@ejohnsondev.com",
             picture='http://vignette3.wikia.nocookie.net/the-leftovers/images/6/61/JohnMurphyProfile.png'
                     '/revision/latest?cb=20160704044731')
session.add(User1)
session.commit()

User2 = User(name="Ophelia Lancaster", email="olancaster@ejohnsondev.com",
             picture='https://pbs.twimg.com/profile_images/378800000497108800'
                     '/eedf5d171b33f4e6ef91a739458286c0_400x400.jpeg')
session.add(User2)
session.commit()

# Add some books to the library
book1 = Books(title="The Stand", author="Stephen King",
              description="When a man escapes from a biological testing facility, he sets in motion a deadly domino "
                          "effect, spreading a mutated strain of the flu that will wipe out 99 percent of humanity "
                          "within a few weeks. The survivors who remain are scared, bewildered, and in need of a "
                          "leader. Two emerge--Mother Abagail, the benevolent 108-year-old woman who urges them "
                          "to build a community in Boulder, Colorado; and Randall Flagg, the nefarious 'Dark Man,'"
                          " who delights in chaos and violence.")
session.add(book1)
session.commit()

book2 = Books(title="The Tao of Bill Murray", author="Gavin Edwards",
              description="For the Bill Murray fan in all of us, this epic collection of 'Bill Murray stories' - many "
                          "reported for the first time here - distills a set of guiding principles out of his "
                          "extraordinary ability to infuse the everyday with surprise, absurdity, and wonder.")
session.add(book2)
session.commit()

book3 = Books(title="The Phoenix Project", author="Gene Kim",
              description="In a fast-paced and entertaining style, three luminaries of the DevOps movement deliver "
                          "a story that anyone who works in IT will recognize. Readers will not only learn how to "
                          "improve their own IT organizations, they'll never view IT the same way again.")
session.add(book3)
session.commit()

book4 = Books(title="Cracking the Coding Interview: 189 Programming Questions and Solutions",
              author="Gayle Laakmann McDowell",
              description="Learn how to uncover the hints and hidden details in a question, discover how to "
                          "break down a problem into manageable chunks, develop techniques to unstick yourself "
                          "when stuck, learn (or re-learn) core computer science concepts, "
                          "and practice on 189 interview questions and solutions.")
session.add(book4)
session.commit()

book5 = Books(title="The Millionaire Next Door: The Surprising Secrets of America's Wealthy",
              author="Thomas J. Stanley",
              description="The bestselling The Millionaire Next Door identifies seven common traits that show up "
                          "again and again among those who have accumulated wealth. Most of the truly wealthy in "
                          "this country don't live in Beverly Hills or on Park Avenue-they live next door. "
                          "This new edition, the first since 1998, includes a new foreword for the twenty-first "
                          "century by Dr. Thomas J. Stanley.")
session.add(book5)
session.commit()

book6 = Books(title="A People's History of the United States", author="Howard Zinn",
              description="Covering Christopher Columbus's arrival through President Clinton's first term, "
                          "A People's History of the United States, which was nominated for the American Book Award "
                          "in 1981, features insightful analysis of the most important events in our history. ")
session.add(book6)
session.commit()

book7 = Books(title="Moby Dick", author="Herman Melville",
              description="Ignoring prophecies of doom, the seafarer Ishmael joins the crew of a whaling expedition "
                          "that is an obsession for the ship's captain, Ahab. Once maimed by the White Whale, "
                          "Moby Dick, Ahab has set out on a voyage of revenge. With godlike ferocity, he surges into "
                          "dangerous waters - immune to the madness of his vision, "
                          "refusing to be bested by the forces of nature.")
session.add(book7)
session.commit()

book8 = Books(title="Meditations", author="Marcus Aurelius",
              description="One of the world's most famous and influential books, Meditations, by the Roman emperor "
                          "Marcus Aurelius (A.D. 121-180), incorporates the stoic precepts he used to cope with his "
                          "life as a warrior and administrator of an empire. Ascending to the imperial throne in "
                          "A.D. 161, Aurelius found his reign beset by natural disasters and war. In the wake of "
                          "these challenges, he set down a series of private reflections, outlining a philosophy "
                          "of commitment to virtue above pleasure and tranquility above happiness.")
session.add(book8)
session.commit()

book9 = Books(title="Leviathan Wakes", author="James S. A. Corey",
              description="Two hundred years after migrating into space, mankind is in turmoil. When a reluctant "
                          "ship's captain and washed-up detective find themselves involved in the case of a missing "
                          "girl, what they discover brings our solar system to the brink of civil war, "
                          "and exposes the greatest conspiracy in human history.")
session.add(book9)
session.commit()

book10 = Books(title="The Brothers Karamazov", author="Fyodor Dostoyevsky",
              description="The Brothers Karamazov is a passionate philosophical novel set in 19th century Russia, "
                          "that enters deeply into the ethical debates of God, free will and morality. It is a "
                          "spiritual drama of moral struggles concerning faith, doubt, and reason, set against a "
                          "modernizing Russia. A towering masterpiece of literature, philosophy, psychology, "
                          "and religion, The Brothers Karamazov tells the story of intellectual Ivan, sensual Dmitri, "
                          "and idealistic Alyosha Karamazov, who collide in the wake of their despicable "
                          "father's brutal murder.")
session.add(book10)
session.commit()


# Add books to user libraries
user_book1 = User_Books(user_id=1,book_id=1,status="In Progress",notes="Wow, what a thrilling book!")
session.add(user_book1)
session.commit()

user_book2 = User_Books(user_id=2,book_id=4,status="Read",notes="So glad I read this.  Wonderful prep book.")
session.add(user_book2)
session.commit()

user_book3 = User_Books(user_id=2,book_id=7,status="Abandoned",notes="This book will always be my White Whale...")
session.add(user_book3)
session.commit()

user_book4 = User_Books(user_id=1,book_id=7,status="Read",notes="Finally finished it.  It's a real chore, and I "
                                                                "do not recommend it for casual enjoyment.")
session.add(user_book4)
session.commit()

user_book5 = User_Books(user_id=1,book_id=9,status="Unread",notes="My wife read this and recommended.  Looking"
                                                                  "forward to starting it!")
session.add(user_book5)
session.commit()

user_book6 = User_Books(user_id=2,book_id=10,status="In Progress",notes="A very challenging read, but worth it so far.")
session.add(user_book6)
session.commit()

print("Created library!")
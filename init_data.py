#!usr/bin/env python

from database_setup import Users, Base, Items, Categories
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


engine = create_engine(
    'sqlite:///catalog.db',
    connect_args={'check_same_thread': False})

# Bind the above engine to a session.
Session = sessionmaker(bind=engine)

# Create a Session object.
session = Session()

user = Users(
    name='FirstName LastName',
    email='firstName.lastName@gmail.com'
)

session.add(user)
session.commit()

# Categories
CATEGORIES = [
    'Education',
    'Business',
    'Lifestyle',
    'Entertainment',
    'Music & Audio',
    'Tools',
    'Books & Reference',
    'Health & Fitness',
    'Shopping',
    'Other',
    'Social'
]

for idx, name in enumerate(CATEGORIES):
    category = Categories(name=name, user_id=1)
    session.add(category)
    session.commit()

    print str(idx) + ' ' + name

    if name == 'Social':
        item = Items(
            name='Instagram',
            description="Instagram is a simple way to capture and share "
            "the world's moments. Follow your friends and family to see "
            "what they're up to, and discover accounts from all over the "
            "world that are sharing things you love. Join the community "
            " of over 1 billion people and express yourself by sharing all "
            " the moments of your day - the highlights and everything in "
            " between, too.",
            category_id=idx+1,
            user_id=1
        )

        session.add(item)
        session.commit()

    if name == 'Education':
        item = Items(
            name='Quizlet',
            description="Quizlet is the easiest way to practice and "
            "master what you're learning. Create your own flashcards "
            "and study sets or choose from millions created by other "
            "students - it's up to you. More than 30 million students "
            "study with Quizlet each month because it's the leading "
            "education and flashcard app that makes studying languages,"
            " history, vocab and science simple and effective. And "
            "it's free!",
            category_id=idx+1,
            user_id=1
        )

        session.add(item)
        session.commit()

    if name == 'Music & Audio':
        item = Items(
            name='Spotify',
            description="With Spotify, you have access to a world "
            "of music and podcasts. You can listen to artists and "
            "albums, or create your own playlist of your "
            "favorite songs. Want to discover new music? Choose a "
            "ready-made playlist that suits your mood or get personalized"
            " recommendations",
            category_id=idx+1,
            user_id=1
        )

        session.add(item)
        session.commit()

print('Finished populating the database!')

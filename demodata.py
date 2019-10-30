#! /usr/bin/env python

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///appdata.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create user
User1 = User(
    name="Party Goer",
    email="partygoer@gmail.com",
    picture=(
        'https://pbs.twimg.com/profile_images/2671170543/'
        '18debd694829ed78203a5a36dd364160_400x400.png')
    )

session.add(User1)
session.commit()


# Event locations for photography
category1 = Category(
    user_id=1,
    slug="photography",
    name="Photography"
)

session.add(category1)
session.commit()


location1 = Item(
    user_id=1,
    slug="eye-contact",
    name="Eye contact",
    description="A small gallery hosting new photo exhibitions every month",
    address="Auge str. 187, 10961 Berlin",
    category=category1
)

session.add(location1)
session.commit()

location2 = Item(
    user_id=1,
    slug="camera-soul",
    name="Camera soul",
    description="A photo gallery focused on conceptual photography",
    address="Jeben str. 2-3, 10623 Berlin",
    category=category1
)

session.add(location2)
session.commit()

location3 = Item(
    user_id=1,
    slug="see-and-feel",
    name="See&Feel",
    description="An art space for audio-visual installations and workshops",
    address="Yuno str. 2, 10643 Berlin",
    category=category1
)

session.add(location3)
session.commit()

location4 = Item(
    user_id=1,
    slug="p-i-b",
    name="PiB",
    description="Best works of young Berlin photo and visual artists",
    address="Frage str. 3, 10613 Berlin",
    category=category1
)

session.add(location4)
session.commit()


# Cinema locations
category2 = Category(
    user_id=1,
    slug="cinema",
    name="Cinema"
)

session.add(category2)
session.commit()


location1 = Item(
    user_id=1,
    slug="urban-kino",
    name="Urban Kino",
    description="A home for festival film lovers in the heart of Berlin",
    address="Urban str. 17, 10951 Berlin",
    category=category2
)

session.add(location1)
session.commit()

location2 = Item(
    user_id=1,
    slug="no-more-youtube",
    name="NoMoreYoutube",
    description="An independent cinema venue for classic movies",
    address="Hugo str. 13, 10123 Berlin",
    category=category2
)

session.add(location2)
session.commit()

location3 = Item(
    user_id=1,
    slug="tsss",
    name="Tsss",
    description="Silent movies with live music",
    address="Laut str. 12, 10693 Berlin",
    category=category2
)

session.add(location3)
session.commit()

location4 = Item(
    user_id=1,
    slug="pop-up-kino",
    name="PopUp Kino",
    description="An art space for young filmmakers",
    address="Uphill str. 43, 10223 Berlin",
    category=category2
)

session.add(location4)
session.commit()

location5 = Item(
    user_id=1,
    slug="size-does-not-matter",
    name="Size doesn't matter",
    description="Short films laboratory and cinema hall",
    address="Long str. 43, 11623 Berlin",
    category=category2
)

session.add(location5)
session.commit()


# Music venues
category3 = Category(
    user_id=1,
    slug="music",
    name="Music"
)

session.add(category3)
session.commit()


location1 = Item(
    user_id=1,
    slug="shooom",
    name="Shooom",
    description="A small studio for experimental music",
    address="Pferde str. 17, 10961 Berlin",
    category=category3
)

session.add(location1)
session.commit()

location2 = Item(
    user_id=1,
    slug="trauma-bar",
    name="Trauma bar",
    description="A cosy bar with live music and DJ sets",
    address="Graffe str. 73, 10123 Berlin",
    category=category3
)

session.add(location2)
session.commit()

location3 = Item(
    user_id=1,
    slug="kling-klang",
    name="KlingKlang",
    description="Jazz evenings with the best French wine",
    address="Klock str. 32, 10613 Berlin",
    category=category3
)

session.add(location3)
session.commit()

location4 = Item(
    user_id=1,
    slug="lass-uns-treffen",
    name="Lass uns treffen",
    description="Local Berlin musicians playing every evening",
    address="Ultra str. 38, 10616 Berlin",
    category=category3
)

session.add(location4)
session.commit()


# Event locations for dance performances
category4 = Category(
    user_id=1,
    slug="dance",
    name="Dance"
)

session.add(category4)
session.commit()


location1 = Item(
    user_id=1,
    slug="tuck-your-toes",
    name="Tuck your toes",
    description="A contemporary dance studio with and weekly performances",
    address="Herz str. 87, 10061 Berlin",
    category=category4
)

session.add(location1)
session.commit()

location2 = Item(
    user_id=1,
    slug="kizzz",
    name="Kizzz",
    description="A nice kizomba venue with free drinks",
    address="Gott str. 2-3, 10123 Berlin",
    category=category4
)

session.add(location2)
session.commit()

location3 = Item(
    user_id=1,
    slug="zu-dritt",
    name="ZuDritt",
    description="A charming tango studio direct on the Landwerk channel",
    address="Fort str. 32, 10143 Berlin",
    category=category4
)

session.add(location3)
session.commit()

location4 = Item(
    user_id=1,
    slug="gaga-dance",
    name="GgDnc",
    description="Gaga workshops and courses",
    address="Koss str. 23, 10613 Berlin",
    category=category4
)

session.add(location4)
session.commit()

location5 = Item(
    user_id=1,
    slug="exstatic-dance-berlin",
    name="ExstaticDanceBerlin",
    description="Freestyle dance evenings with live DJ sets",
    address="Ex str. 53, 10623 Berlin",
    category=category4
)

session.add(location5)
session.commit()

location6 = Item(
    user_id=1,
    slug="ballet-and-belly",
    name="Ballet&Belly",
    description="A unique combination of ballet and belly dance",
    address="Tanz str. 32, 10913 Berlin",
    category=category4
)

session.add(location6)
session.commit()


# Theaters
category5 = Category(
    user_id=1,
    slug="theater",
    name="Theater"
)

session.add(category5)
session.commit()


location1 = Item(
    user_id=1,
    slug="un-theater",
    name="UnTheater",
    description="A young Berlin theater performing on the edge of genres",
    address="Kleine str. 87, 10961 Berlin",
    category=category5
)

session.add(location1)
session.commit()

location2 = Item(
    user_id=1,
    slug="you-14",
    name="You14",
    description="A youth theater with plays created and performed by teens",
    address="Erwachsene str. 283, 10623 Berlin",
    category=category5
)

session.add(location2)
session.commit()

location3 = Item(
    user_id=1,
    slug="dudu",
    name="Dudu",
    description="A drama therapy studio with the focus on theater techniques",
    address="Duden str. 22, 10643 Berlin",
    category=category5
)

session.add(location3)
session.commit()


print("added locations!")

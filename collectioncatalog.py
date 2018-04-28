# coding=utf-8
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, StudioItem

engine = create_engine('sqlite:///collectioncatalog.db')
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

# Menu for Spin
Category1 = Category(user_id=1, name="Spin")

session.add(Category1)
session.commit()


studioItem1 = StudioItem(user_id=1, name="Soul Cycle",
                         description="revolutionized indoor cycling"
                                     "and taken the world of "
                                     "fitness by storm. 45 minutes"
                                     " to take your journey. Change"
                                     " your body. Find your SOUL",
                         price="$30.00",
                         Address="401 Congress Ave Austin TX 78701",
                         category=Category1)

session.add(studioItem1)
session.commit()

studioItem2 = StudioItem(user_id=1,
                         name="Define",
                         price="$30.00",
                         description=" the key to making all of your other"
                                     " dreams a reality",
                         Address="Ste. K, 809 South Lamar Boulevard,"
                                 "Austin, TX, 78704",
                         category=Category1)

session.add(studioItem2)
session.commit()

studioItem3 = StudioItem(user_id=1,
                         name="Flywheel",
                         description="Flywheel offers challenging workouts,"
                                     " performance tracking, and a passionate"
                                     "community of over half a million"
                                     "athletes.",
                         price="$30.00",
                         Address="3220 Amy Donovan Plaza Ste. 128, Austin,"
                                 " Texas 78758",
                         category=Category1)

session.add(studioItem3)
session.commit()

studioItem4 = StudioItem(user_id=1,
                         name="Love Cycle",
                         description="an INTENSE 45-minute workout, committed"
                                     "to COMMUNITY contribution, aimed to "
                                     "TREAT all guests as personal friends,"
                                     "INSPIRE with awesome instructors and"
                                     "unite us all as a TEAM.",
                         price="$17.00",
                         Address=" 507 Pressler St #900, Austin, TX 78703",
                         category=Category1)

session.add(studioItem4)
session.commit()


# Menu for Yoga
Category2 = Category(user_id=1, name="Yoga")

session.add(Category2)
session.commit()

studioItem1 = StudioItem(user_id=1, name="Wanderlust Yoga",
                         description="inspired to bring the extraordinary"
                                     "aspects of the Wanderlust Festival"
                                     "into the everyday lives of the people"
                                     " who live,work and visit Austin, Texas.",
                         price="$7.99",
                         Address="206 E 4th St, Austin, TX 78701",
                         category=Category2)

session.add(studioItem1)
session.commit()

studioItem2 = StudioItem(user_id=1,
                         name="Black Swan Yoga",
                         description="  ou'll find warm and expansive lobby"
                                     "-free studios with custom featured"
                                     "artwork, luminous lighting, and music"
                                     " curated by the teachers themselves.",
                         price="$25.00",
                         Address="403 Orchard St, Austin, TX 78703",
                         category=Category2)

session.add(studioItem2)
session.commit()

studioItem3 = StudioItem(user_id=1,
                         name="TreeHouse Yoga",
                         description="those just wanting to find a bit more"
                                     "stillness in their lives We elevate"
                                     "communities by providing tools to create"
                                     " transformationin the lives",
                         price="$15.00",
                         Address="2525 Wallingwood Dr #300, Austin, TX 78746",
                         category=Category2)

session.add(studioItem3)
session.commit()


# Menu for Kickboxing
Category3 = Category(user_id=1, name="Kickboxing")

session.add(Category3)
session.commit()

studioItem1 = StudioItem(user_id=1,
                         name="Fight Club Austin",
                         description="Cardio kickboxing class aimed at "
                                     "achieving ultimate results.",
                         price="$20.00",
                         Address="2222 Rio Grande St #170, Austin, TX 78705",
                         category=Category3)

session.add(studioItem1)
session.commit()

studioItem2 = StudioItem(user_id=1,
                         name="ILoveKickboxing Austin",
                         description="a common Chinese dumpling which "
                                     "generally"
                                     " consists of minced meat and finely"
                                     "chopped vegetables wrapped into a piece"
                                     " of dough skin. The skin can be either"
                                     "thin and elastic or thicker.",
                         price="$10.00",
                         Address="1700 S Lamar Blvd #203, Austin, TX 78704",
                         category=Category3)

session.add(studioItem2)
session.commit()

studioItem3 = StudioItem(user_id=1,
                         name="Austin Kickboxing Academy",
                         description="We make this fun and challenging class"
                                     " available to everyone!",
                         price="$10.00",
                         Address="3232 E Cesar Chavez St, Austin, TX 78702",
                         category=Category3)

session.add(studioItem3)
session.commit()

# Menu for Barre
Category4 = Category(user_id=1, name="Barre")

session.add(Category4)
session.commit()

studioItem1 = StudioItem(user_id=1,
                         name="The Barre Code",
                         description="The most efficient and results for"
                                     "driven womens fitness program",
                         price="$17.00",
                         Address="2300 S Lamar Blvd, Austin, TX 78704",
                         category=Category4)

session.add(studioItem1)
session.commit()

studioItem2 = StudioItem(user_id=1,
                         name="Pure Barre",
                         description="In less than an hour you will achieve a"
                                     "full-body workout concentrating on the"
                                     "areas women struggle with the most:"
                                     "hips,thighs, seat, abdominals and arms.",
                         price="$7.00",
                         Address="10710 Research Blvd #316, Austin, TX 78759",
                         category=Category4)

session.add(studioItem2)
session.commit()

studioItem3 = StudioItem(user_id=1,
                         name="Barre3 Austin",
                         description="Milk snow layered with honey boba,"
                                     "jasmine tea jelly, grass jelly, caramel,"
                                     " cream, and freshly made mochi",
                         price="$20.00",
                         Address="Gables Park Plaza, 115 Sandra Muraida Way, "
                                 "Austin, TX 78703",
                         category=Category4)

session.add(studioItem3)
session.commit()


# Menu for Dance
Category5 = Category(user_id=1, name="Dance")

session.add(Category5)
session.commit()

studioItem1 = StudioItem(user_id=1,
                         name="Austin City Dance Club",
                         description="This is Austin City Dance Club, a non-"
                                     "profit membership organization that "
                                     "specializes in social dancing in "
                                     "Austin, Texas.",
                         price="$15.00",
                         Address="7811 Rockwood Ln, Austin, TX 78757",
                         category=Category5)

session.add(studioItem1)
session.commit()

studioItem2 = StudioItem(user_id=1,
                         name="Dance International",
                         description="We provide a fun, healthy and nurturing"
                                     "environment for you learn to dance."
                                     "Private lessons are also available.",
                         price="$10.00",
                         Address="2417 Buell Ave, Austin, TX 78757",
                         category=Category5)

session.add(studioItem2)
session.commit()

studioItem3 = StudioItem(user_id=1,
                         name="Austin School of Classical Ballet",
                         description="The Austin School of Classical Ballet"
                                     "is committed to providing the finest"
                                     "training available to students "
                                     "interested in the art of ballet.",
                         price="$9.00",
                         Address="4624 Burnet Rd, Austin, TX 78756",
                         category=Category5)

session.add(studioItem3)
session.commit()


print "added menu items!"

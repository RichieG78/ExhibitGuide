"""
Management command to seed the database with dummy exhibit data for testing.

Usage:
    python manage.py seed_data
    python manage.py seed_data --clear   # wipe existing exhibits first
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from exhibits.models import Artist, Artwork, Exhibit, Show
import datetime


SEED_EXHIBITS = [
    {
        "show_name": "Masters of Light",
        "artwork": "The Starry Night",
        "artist": "Vincent van Gogh",
        "medium": "Oil on canvas",
        "dimensions_height": 74,
        "dimensions_width": 92,
        "provenance": (
            "Painted in June 1889 at the Saint-Paul-de-Mausole asylum, Saint-Rémy-de-Provence. "
            "Gifted by Van Gogh to Theo van Gogh, 1889. Acquired by Julien Leclercq, 1900. "
            "Passed to Georgette Agutte. Purchased by Lillie P. Bliss, 1929. "
            "Bequeathed to the Museum of Modern Art, New York, 1941."
        ),
        "price": 0,
        "currency": "USD",
        "tldr": (
            "Van Gogh's swirling nocturnal sky over a sleeping village — one of the most "
            "recognised paintings in Western art."
        ),
        "full_text": (
            "Painted during Van Gogh's voluntary stay at the Saint-Paul-de-Mausole asylum, "
            "The Starry Night depicts the view from his east-facing window just before sunrise, "
            "with the addition of an idealised village. The turbulent, luminous sky dominates "
            "the composition, rendered in thick impasto strokes that seem to pulse with energy. "
            "A cypress tree — a symbol of death and eternity — anchors the foreground. "
            "Van Gogh described the work in letters to his brother Theo as an attempt to express "
            "extreme emotion through colour and form rather than literal representation. "
            "The painting was little appreciated in his lifetime but is now a cornerstone of "
            "Post-Impressionism and an enduring symbol of artistic passion and mental anguish."
        ),
        "audio_url": "https://www.moma.org/audio/playlist/1/tracks/99",
        "video_url": "https://www.youtube.com/watch?v=ubTJI_UphPk",
        "image_url": (
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/"
            "Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-"
            "Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg"
        ),
        "qr_identifier": 1001,
        "publish_date": timezone.make_aware(datetime.datetime(2025, 3, 1, 10, 0, 0)),
    },
    {
        "show_name": "Masters of Light",
        "artwork": "Girl with a Pearl Earring",
        "artist": "Johannes Vermeer",
        "medium": "Oil on canvas",
        "dimensions_height": 45,
        "dimensions_width": 39,
        "provenance": (
            "Painted c. 1665, The Hague. First recorded at auction in The Hague, 1881, "
            "purchased by A. A. des Tombe for 2 guilders and 30 cents. "
            "Bequeathed to the Mauritshuis, The Hague, 1902, where it has remained."
        ),
        "price": 0,
        "currency": "EUR",
        "tldr": (
            "Often called the 'Mona Lisa of the North', Vermeer's enigmatic portrait "
            "captivates with its direct gaze and luminous pearl."
        ),
        "full_text": (
            "Girl with a Pearl Earring is a tronie — a Dutch Golden Age study of a figure type "
            "rather than a specific portrait. The identity of the sitter remains unknown, "
            "though many theories abound. Vermeer's mastery is evident in the subtle gradation "
            "of light across the girl's face, the soft shadow on her collar, and the way the "
            "pearl earring catches the light with a single precise highlight. "
            "The deep black background, unusual for Vermeer, concentrates all attention on the "
            "face and creates a sense of intimacy. The girl's parted lips and turned gaze "
            "suggest a fleeting moment caught — a technique that gives the work its "
            "extraordinary psychological immediacy. Tracy Chevalier's 1999 novel of the same "
            "name imagined a fictional story behind the painting, bringing it global recognition."
        ),
        "audio_url": "https://www.mauritshuis.nl/en/our-collection/artworks/670-girl-with-a-pearl-earring/",
        "video_url": "https://www.youtube.com/watch?v=aNSfmxSP5Oo",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/0f/1665_Girl_with_a_Pearl_Earring.jpg",
        "qr_identifier": 1002,
        "publish_date": timezone.make_aware(datetime.datetime(2025, 3, 1, 10, 0, 0)),
    },
    {
        "show_name": "Masters of Light",
        "artwork": "The Great Wave off Kanagawa",
        "artist": "Katsushika Hokusai",
        "medium": "Woodblock print; ink and colour on paper",
        "dimensions_height": 25,
        "dimensions_width": 37,
        "provenance": (
            "Published by Nishimuraya Yohachi (Eijudō), Edo (Tokyo), c. 1831. "
            "Multiple impressions exist; notable examples held at the Metropolitan Museum "
            "of Art, New York; the Art Institute of Chicago; and the British Museum, London."
        ),
        "price": 250000,
        "currency": "GBP",
        "tldr": (
            "Hokusai's iconic wave — foam claws reaching for three fishing boats as "
            "Mount Fuji sits serenely in the distance."
        ),
        "full_text": (
            "Part of Hokusai's series Thirty-six Views of Mount Fuji, The Great Wave is the "
            "most celebrated ukiyo-e print ever made. Hokusai composed the image so that the "
            "claw-like crest of the wave frames Mount Fuji, diminished in the background — "
            "a visual metaphor for the power of nature over human endeavour. "
            "Three oshiokuri-bune (fast cargo boats) fight to keep their prows into the wave. "
            "The distinctive Prussian blue pigment, only recently available to Japanese "
            "printmakers, gives the work its vivid, modern quality. "
            "After Commodore Perry's 1854 expedition opened Japan to the West, Japanese prints "
            "flooded into Europe, triggering Japonisme and influencing Monet, Degas, and "
            "Van Gogh. The Great Wave became the emblem of that exchange — a Japanese artwork "
            "that helped reshape Western modernism."
        ),
        "audio_url": "https://www.metmuseum.org/art/collection/search/45434",
        "video_url": "https://www.youtube.com/watch?v=AmHONpJUNoE",
        "image_url": (
            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/"
            "Tsunami_by_hokusai_19th_century.jpg/1280px-Tsunami_by_hokusai_19th_century.jpg"
        ),
        "qr_identifier": 1003,
        "publish_date": timezone.make_aware(datetime.datetime(2025, 3, 1, 10, 0, 0)),
    },
    {
        "show_name": "Colour & Form",
        "artwork": "Water Lilies (Nymphéas)",
        "artist": "Claude Monet",
        "medium": "Oil on canvas",
        "dimensions_height": 90,
        "dimensions_width": 94,
        "provenance": (
            "One of approximately 250 Water Lilies paintings produced by Monet between 1896 "
            "and his death in 1926 at Giverny. This example passed from the artist's estate "
            "to a private French collection, later acquired by a European foundation and "
            "exhibited internationally."
        ),
        "price": 4200000,
        "currency": "GBP",
        "tldr": (
            "Late Monet at his most immersive — the surface of his Giverny pond dissolved "
            "into pure colour and light."
        ),
        "full_text": (
            "Monet began painting the water garden he had created at his home in Giverny in "
            "the mid-1890s and returned to the subject obsessively for the rest of his life, "
            "producing what he called a 'series of water landscapes'. As his eyesight failed "
            "from cataracts, his palette shifted toward warmer oranges and reds, and his "
            "brushwork became increasingly loose and gestural. The works from this late period "
            "anticipate Abstract Expressionism by decades. "
            "Without horizon line or sky, the compositions offer no spatial anchor — the "
            "viewer is drawn into a shimmering, reflective world where sky, clouds, and plants "
            "all exist on the same plane. Monet donated 22 large-format panels to the French "
            "state; they are permanently installed in the Orangerie, Paris. Smaller canvases "
            "from the series appear regularly at auction, where they command among the highest "
            "prices of any Impressionist work."
        ),
        "audio_url": "https://www.artic.edu/artworks/16568/water-lilies",
        "video_url": "https://www.youtube.com/watch?v=RCaOhUGXBdw",
        "image_url": (
            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/"
            "Claude_Monet_-_Water_Lilies_-_1906%2C_Ryerson.jpg/1280px-"
            "Claude_Monet_-_Water_Lilies_-_1906%2C_Ryerson.jpg"
        ),
        "qr_identifier": 1004,
        "publish_date": timezone.make_aware(datetime.datetime(2025, 4, 15, 10, 0, 0)),
    },
    {
        "show_name": "Colour & Form",
        "artwork": "Portrait of Adele Bloch-Bauer I",
        "artist": "Gustav Klimt",
        "medium": "Oil, gold, and silver on canvas",
        "dimensions_height": 138,
        "dimensions_width": 138,
        "provenance": (
            "Commissioned by Ferdinand Bloch-Bauer, Vienna, 1903–07. Seized by the Nazi "
            "regime following the Anschluss, 1938; displayed at the Österreichische Galerie "
            "Belvedere, Vienna as 'Lady in Gold'. Restituted to the Bloch-Bauer heirs after "
            "landmark US Supreme Court ruling, 2004. Purchased by Ronald Lauder for the "
            "Neue Galerie, New York, 2006, for a then-record $135 million."
        ),
        "price": 135000000,
        "currency": "USD",
        "tldr": (
            "Klimt's golden masterpiece — a shimmering fusion of Byzantine mosaic, "
            "Art Nouveau ornament, and intimate portraiture."
        ),
        "full_text": (
            "Klimt spent three years producing this portrait, filling sketchbooks with studies "
            "of Adele Bloch-Bauer — a prominent figure in Viennese cultural life and the only "
            "subject he painted twice. The finished work collapses the boundary between figure "
            "and ground: Adele's face and hands emerge from a sea of gold and geometric pattern "
            "that engulfs her dress, chair, and background equally. "
            "Klimt drew on the Byzantine mosaics he had seen in Ravenna, ancient Egyptian art, "
            "and Japanese lacquerwork to create his distinctive 'golden style'. "
            "The painting's wartime theft and decades-long misattribution as 'Woman in Gold' "
            "made it a symbol of Nazi looting and the struggle for cultural restitution. "
            "Maria Altmann's legal battle to recover the painting — depicted in the 2015 film "
            "Woman in Gold — galvanised international debate about museum ownership of "
            "looted art."
        ),
        "audio_url": "https://www.neuegalerie.org/collection/austrian-art/klimt",
        "video_url": "https://www.youtube.com/watch?v=mA0MtVDOOI0",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/84/Gustav_Klimt_046.jpg",
        "qr_identifier": 1005,
        "publish_date": timezone.make_aware(datetime.datetime(2025, 4, 15, 10, 0, 0)),
    },
    {
        "show_name": "Colour & Form",
        "artwork": "Arrangement in Grey and Black No. 1 (Whistler's Mother)",
        "artist": "James McNeill Whistler",
        "medium": "Oil on canvas",
        "dimensions_height": 144,
        "dimensions_width": 162,
        "provenance": (
            "Painted in London, 1871. Exhibited at the Royal Academy, 1872. "
            "Purchased by the French state, 1891, for 4,000 francs on the urging of Stéphane "
            "Mallarmé. Permanently held at the Musée d'Orsay, Paris."
        ),
        "price": 0,
        "currency": "EUR",
        "tldr": (
            "An austere study in grey and black that became, unexpectedly, one of America's "
            "most sentimental national icons."
        ),
        "full_text": (
            "Whistler painted his mother, Anna McNeill Whistler, when a model failed to show "
            "for a scheduled sitting. His title, Arrangement in Grey and Black No. 1, "
            "announced his belief that a painting's subject should be secondary to its formal "
            "qualities — the artist as composer of visual harmony, not illustrator of content. "
            "The composition is radically flat: a severe profile against a bare grey wall, "
            "broken only by a curtain and a small framed print. "
            "Despite Whistler's intentions, the painting was received as a tender tribute to "
            "motherhood and became embedded in American popular culture, reproduced on "
            "postage stamps and parodied in countless cartoons. "
            "Its influence on American Tonalism and the Aesthetic Movement was substantial, "
            "and it stands as a bridge between Realism and the formalist concerns that would "
            "dominate the following century."
        ),
        "audio_url": "https://www.musee-orsay.fr/en/artworks/arrangement-in-grey-and-black-no-1",
        "video_url": "https://www.youtube.com/watch?v=Yq6C6cZGPBE",
        "image_url": (
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/"
            "Whistlers_Mother_high_res.jpg/1024px-Whistlers_Mother_high_res.jpg"
        ),
        "qr_identifier": 1006,
        "publish_date": timezone.make_aware(datetime.datetime(2025, 4, 15, 10, 0, 0)),
    },
    {
        "show_name": "British Romantics",
        "artwork": "The Fighting Temeraire",
        "artist": "J. M. W. Turner",
        "medium": "Oil on canvas",
        "dimensions_height": 91,
        "dimensions_width": 122,
        "provenance": (
            "Exhibited at the Royal Academy, London, 1839. Turner refused all offers to sell "
            "it during his lifetime, calling it 'my darling'. Bequeathed to the British nation "
            "by Turner on his death in 1851. National Gallery, London, since 1856. "
            "Voted the greatest painting in Britain in a public poll, 2005."
        ),
        "price": 0,
        "currency": "GBP",
        "tldr": (
            "Turner's elegy for the age of sail — a ghostly warship hauled to the breaker's "
            "yard by a squat, belching steam tug at sunset."
        ),
        "full_text": (
            "The Temeraire was a 98-gun ship of the line that played a distinguished role at "
            "the Battle of Trafalgar in 1805, fighting alongside Nelson's Victory. By 1838, "
            "the age of sail was giving way to steam, and the vessel was sold for scrap, "
            "towed up the Thames to Rotherhithe by a steam tug. Turner witnessed or heard of "
            "this journey and transformed it into a meditation on time, progress, and loss. "
            "The warship is rendered in near-transparent whites and silvers, almost ghostly, "
            "while the tug — dark, mechanical, belching fire — represents a modernity that "
            "has no room for such beauty. The sun sets in a furnace of oranges and golds that "
            "feel simultaneously magnificent and funereal. "
            "Turner's handling of atmosphere and light here reaches its most lyrical, and the "
            "work is considered by many critics the apotheosis of British Romantic painting."
        ),
        "audio_url": "https://www.nationalgallery.org.uk/paintings/joseph-mallord-william-turner-the-fighting-temeraire",
        "video_url": "https://www.youtube.com/watch?v=GBxHt44kDYY",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/30/The_Fighting_Temeraire%2C_JMW_Turner%2C_National_Gallery.jpg",
        "qr_identifier": 1007,
        "publish_date": timezone.make_aware(datetime.datetime(2025, 5, 10, 10, 0, 0)),
    },
    {
        "show_name": "British Romantics",
        "artwork": "Ophelia",
        "artist": "Sir John Everett Millais",
        "medium": "Oil on canvas",
        "dimensions_height": 76,
        "dimensions_width": 112,
        "provenance": (
            "Painted 1851–52, London. Exhibited at the Royal Academy, 1852. "
            "Purchased by Henry Farrer, 1852. Acquired by Sir Henry Tate, 1894. "
            "Presented to the nation; Tate Britain, London, since 1894."
        ),
        "price": 0,
        "currency": "GBP",
        "tldr": (
            "The Pre-Raphaelite masterpiece of Shakespeare's drowning Ophelia, "
            "set in a botanically precise English riverbank painted outdoors over months."
        ),
        "full_text": (
            "Millais spent the summer of 1851 painting the riverbank near Ewell, Surrey, "
            "meticulously documenting every plant, flower, and insect in the Pre-Raphaelite "
            "commitment to truth to nature. The following winter, Elizabeth Siddal — Millais's "
            "model and later Dante Gabriel Rossetti's wife — posed for hours in a heated bath "
            "to recreate Ophelia's drowning pose, falling ill with a severe cold as a result. "
            "The finished painting layers botanical symbolism throughout: pansies for "
            "remembrance, violets for faithfulness, roses for love and beauty, a poppy for "
            "death. Ophelia's open mouth and wide eyes are ambiguous — serenity or terror? "
            "The work caused a sensation at the Royal Academy and became one of the defining "
            "images of Pre-Raphaelitism. Its influence on later depictions of feminine tragedy "
            "— in art, photography, and cinema — has been immense."
        ),
        "audio_url": "https://www.tate.org.uk/art/artworks/millais-ophelia-n01506",
        "video_url": "https://www.youtube.com/watch?v=dPZ2ERxzFqg",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/94/John_Everett_Millais_-_Ophelia_-_Google_Art_Project.jpg",
        "qr_identifier": 1008,
        "publish_date": timezone.make_aware(datetime.datetime(2025, 5, 10, 10, 0, 0)),
    },
    {
        "show_name": "British Romantics",
        "artwork": "The Birth of Venus",
        "artist": "Sandro Botticelli",
        "medium": "Tempera on canvas",
        "dimensions_height": 173,
        "dimensions_width": 279,
        "provenance": (
            "Painted c. 1484–86, Florence, likely commissioned by the Medici family. "
            "Recorded in the Villa di Castello (Lorenzo di Pierfrancesco de' Medici) by 1550. "
            "Transferred to the Uffizi Gallery, Florence, 1815, where it remains."
        ),
        "price": 0,
        "currency": "EUR",
        "tldr": (
            "Botticelli's Venus rises from the sea on a scallop shell — the defining image "
            "of Renaissance beauty and humanist idealism."
        ),
        "full_text": (
            "One of the first large-scale mythological paintings produced since antiquity, "
            "The Birth of Venus signals the Florentine Renaissance's embrace of classical "
            "subject matter and the nude as a vehicle for ideal beauty. "
            "Venus stands in the contrapposto pose of a classical Venus Pudica, her golden "
            "hair blown by Zephyr (the west wind), who carries the rose-scented breeze. "
            "A Hora (the goddess of seasons) rushes to clothe her with a flower-scattered "
            "mantle. Botticelli's Venus has been identified with Simonetta Vespucci, "
            "celebrated beauty of Florentine society and beloved of Giuliano de' Medici. "
            "The painting's exquisite linearity — figures defined by sinuous contour rather "
            "than modelling — derives from Botticelli's training as a goldsmith and his "
            "admiration for the sculptor Antonio del Pollaiuolo. "
            "Few paintings have exercised greater influence on the Western ideal of feminine "
            "beauty or been more widely reproduced."
        ),
        "audio_url": "https://www.uffizi.it/en/artworks/birth-of-venus",
        "video_url": "https://www.youtube.com/watch?v=iDMIBMQkBBc",
        "image_url": (
            "https://upload.wikimedia.org/wikipedia/commons/0/0b/"
            "Sandro_Botticelli_-_La_nascita_di_Venere_-_Google_Art_Project_-_edited.jpg"
        ),
        "qr_identifier": 1009,
        "publish_date": timezone.make_aware(datetime.datetime(2025, 5, 10, 10, 0, 0)),
    },
    {
        "show_name": "Contemporary Visions",
        "artwork": "No. 61 (Rust and Blue)",
        "artist": "Mark Rothko",
        "medium": "Oil on canvas",
        "dimensions_height": 294,
        "dimensions_width": 232,
        "provenance": (
            "Painted 1953. Exhibited at the Art Institute of Chicago, 1954. "
            "Acquired by a private American collector. Sold at Christie's New York, 2012 "
            "for $75.1 million. Currently in a private European collection."
        ),
        "price": 75000000,
        "currency": "USD",
        "tldr": (
            "Two luminous colour fields — warm rust above cool blue — that Rothko "
            "intended to induce the trembling threshold of religious experience."
        ),
        "full_text": (
            "Mark Rothko rejected the label 'abstract painter', insisting his large colour-field "
            "canvases were 'dramas' concerned with human emotion in its most elemental form: "
            "tragedy, ecstasy, doom. He instructed viewers to stand close — 18 inches — so "
            "the colours could envelope peripheral vision and bypass intellectual detachment. "
            "No. 61 (Rust and Blue) exemplifies his mature method: thin, luminous veils of "
            "colour built up through multiple translucent layers, the edges of each rectangle "
            "left soft and breathing. The warm rust form above and the deep blue below create "
            "a tension that Rothko compared to 'the silence before a thunderstorm'. "
            "He was reportedly moved to tears on hearing that viewers wept before his paintings "
            "— for him, this was proof the transaction he sought had taken place. "
            "When visiting Rothko's work, give yourself time. Sit or stand close. Let the "
            "colour do its work."
        ),
        "audio_url": "https://www.moma.org/collection/works/79878",
        "video_url": "https://www.youtube.com/watch?v=ItOGcuFJqvc",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/39/N%C2%BA_24_%28Brown%2C_Black_and_Blue%29%2C_Mark_Rothko%2C_Paintings_in_the_San_Francisco_Museum_of_Modern_Art%2C_SFMOMA_12.jpg",
        "qr_identifier": 1010,
        "publish_date": timezone.make_aware(datetime.datetime(2025, 6, 1, 10, 0, 0)),
    },
]


class Command(BaseCommand):
    """Create a deterministic sample dataset for local demos and manual testing."""

    help = "Seed the database with 10 dummy exhibits for testing."

    def add_arguments(self, parser):
        """Register optional command flags controlling seed behavior."""
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing exhibits before seeding.",
        )
        parser.add_argument(
            "--username",
            type=str,
            default="admin",
            help="Username of the owner user (created if it doesn't exist). Default: admin",
        )

    def handle(self, *args, **options):
        """Seed artists, artworks, shows, and exhibits using idempotent upserts."""
        if options["clear"]:
            count, _ = Exhibit.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {count} existing exhibit(s)."))

        # Get or create the owner user
        username = options["username"]
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": f"{username}@example.com",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            # Local-only convenience password so evaluators can immediately sign in.
            user.set_password("password123")
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created superuser '{username}' with password 'password123'."
                )
            )
        else:
            self.stdout.write(f"Using existing user '{username}'.")

        created_count = 0
        for data in SEED_EXHIBITS:
            artist_name = data['artist'].strip()
            name_parts = artist_name.split(' ', 1)
            artist_firstname = name_parts[0]
            artist_lastname = name_parts[1] if len(name_parts) > 1 else ''
            artist, _ = Artist.objects.get_or_create(
                firstname=artist_firstname,
                lastname=artist_lastname,
                defaults={'nationality': ''},
            )

            show, _ = Show.objects.get_or_create(
                show_name=data['show_name'],
                defaults={
                    'start_date': data['publish_date'].date(),
                    'end_date': data['publish_date'].date(),
                },
            )

            artwork, _ = Artwork.objects.get_or_create(
                title=data['artwork'],
                artist=artist,
                defaults={
                    'medium': data['medium'],
                    'dimensions_height': data['dimensions_height'],
                    'dimensions_width': data['dimensions_width'],
                    'provenance': data['provenance'],
                },
            )

            exhibit_defaults = {
                'gallery_name': 'Hargreaves Fine Art',
                'show': show,
                'artwork': artwork,
                'price': data['price'],
                'currency': data['currency'],
                'tldr': data['tldr'],
                'full_text': data['full_text'],
                'audio_url': data['audio_url'],
                'video_url': data['video_url'],
                'image_url': data['image_url'],
                'publish_date': data['publish_date'],
                'user': user,
            }

            # Use qr_identifier as the stable idempotency key to avoid unique-key collisions.
            exhibit, created = Exhibit.objects.get_or_create(
                qr_identifier=data['qr_identifier'],
                defaults=exhibit_defaults,
            )

            if not created:
                for field_name, field_value in exhibit_defaults.items():
                    setattr(exhibit, field_name, field_value)
                exhibit.save()
            if created:
                created_count += 1
                self.stdout.write(f"  ✓ Created: {exhibit}")
            else:
                self.stdout.write(f"  – Skipped (already exists): {exhibit}")

        self.stdout.write(
            self.style.SUCCESS(f"\nDone. {created_count} exhibit(s) created.")
        )

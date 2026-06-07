from dataclasses import dataclass
from typing import List, Dict

CTA_DOC_ID = "10xcZ9EhROBdzCHbs4MAm9asUWKloYXRDw7qGDBnyqUQ"

@dataclass(frozen=True)
class ProgramConfig:
    key: str
    label: str
    playlist_id: str
    scheduled_day: str
    description: str


PROGRAMS: List[ProgramConfig] = [
    ProgramConfig(
        key="rwwa",
        label="Remembering Who We Are",
        playlist_id="PL43tb1D5I9UYq80BtCUNR2jDtbflfUJS9",
        scheduled_day="Wednesday",
        description=(
            "At Upbuild, we are committed to creating a space for connection, reflection, and "
            "spiritual grounding. We invite you to join us in a weekly community gathering to "
            "pause and reconnect with a deeper perspective. Each session begins with a brief "
            "reading—an excerpt from a book, a poem, a verse from a spiritual text—and flows "
            "into a discussion around the reading's meaning and how it may resonate with our "
            "lives. Together, we explore how to rise above the pull of the material world, "
            "purify our consciousness, and go deeper into who we really are, all while immersing "
            "ourselves in the enriching presence of spiritual sanga (association). "
            "You can register here: https://www.upbuild.com/remembering-who-we-are"
        ),
    ),
    ProgramConfig(
        key="morning_rounds",
        label="Morning Rounds",
        playlist_id="PL43tb1D5I9UZE5Mlvg1NRGmTPtS8KTOAi",
        scheduled_day="Tuesday",
        description=(
            "Morning Rounds is a devotional reflection series with Hari, exploring Bhakti Yoga, "
            "the Holy Name, scripture, and the inner life of Krishna consciousness.\n\n"
            "\U0001f310 Upbuild: https://upbuild.com\n"
            "\U0001f399️ Upbuild Podcast: https://upbuild.com/podcast\n"
            "\U0001f4c5 Join Morning Rounds live: https://upbuild.com/morning-rounds\n\n"
            "Subscribe for new episodes. #MorningRounds #BhaktiYoga #KrishnaConsciousness"
        ),
    ),
    ProgramConfig(
        key="cta",
        label="Call to Awaken",
        playlist_id="PL43tb1D5I9UZ89zKaxt-1uzHvSEn5snP7",
        scheduled_day="Tuesday",
        description=(
            "The Call to Awaken is the foundation for all that we do at Upbuild, and it's "
            "very close to our hearts. The course is a journey through the Bhagavad-Gita designed "
            "to introduce and integrate the core concepts of this sacred text into the fabric of "
            "our daily lives. It is tailored for those without prior spiritual knowledge or those "
            "in the early stages of a spiritual path. It is meant for those seeking answers to the "
            "deep questions of life and wanting to be spiritual practitioners in our modern society. "
            "We weave together movie and TV clips, quotations from contemporary scientists and "
            "ancient philosophers, and personal anecdotes to bring home the universal and timeless "
            "nature of the Gita's key concepts."
        ),
    ),
    ProgramConfig(
        key="library_live",
        label="Enneagram Library Live",
        playlist_id="PL43tb1D5I9UZMMwswTSYEYRWogIJ4x1Z4",
        scheduled_day="Thursday",
        description=(
            "Welcome to the Upbuild Enneagram Library Live.\n\n"
            "These classes are part of an ongoing exploration of the Enneagram through the lens "
            "of self-awareness, inner growth, leadership, relationships, and spiritual development. "
            "At Upbuild, we use the Enneagram as a tool for understanding the deeper patterns, "
            "motivations, fears, and strategies that shape our lives.\n\n"
            "These classes are designed to loosen the grip of who we think we should be (the ego) "
            "so we can become who we actually are (the self).\n\n"
            "Learn more about Upbuild and explore additional Enneagram resources: "
            "https://www.upbuild.com/enneagram\n\n"
            "Listen to the Upbuild Enneagram Podcast:\n"
            "Apple Podcasts: https://podcasts.apple.com/us/podcast/upbuild-enneagram/id1528797529\n"
            "Spotify: https://open.spotify.com/show/0QsKoEDm19z9kQLI9kTkbz"
        ),
    ),
    ProgramConfig(
        key="bhakti_sastri",
        label="Bhakti Sastri",
        playlist_id="PL43tb1D5I9Ua4WnMFTMIRUOR1A_pE48Je",
        scheduled_day="Wednesday",
        description="",
    ),
    ProgramConfig(
        key="committed_bhakti",
        label="Committed Bhakti",
        playlist_id="PL43tb1D5I9UZ9keqCupQFDEil4S6NkzM_",
        scheduled_day="Friday",
        description=(
            "Committed Bhakti is an immersive journey into the philosophy, practice, and culture "
            "of Krishna Consciousness, helping participants deepen their understanding of Bhakti "
            "and cultivate a more meaningful relationship with Krishna."
        ),
    ),
]

PROGRAM_BY_KEY: Dict[str, ProgramConfig] = {p.key: p for p in PROGRAMS}
PROGRAM_LABELS: List[str] = [p.label for p in PROGRAMS]

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from .models import Link, Transition


async def create_link(session: AsyncSession, link: str) -> tuple[str, str]:
    """
    Creates a new link entry in the database.

    Parameters:
        session (AsyncSession): The async session to interact with the database.
        link (str): The original link to be stored.

    Returns:
        tuple[str, str]: A tuple containing the short link and access key generated for the new entry.
    """
    db_link = Link(original_link=link.original_link)
    session.add(db_link)
    await session.commit()
    await session.refresh(db_link)
    return db_link.short_link, db_link.access_key


async def get_link_by_short_link(session: AsyncSession, short_link: str) -> Link | None:
    """
    Retrieves the original link associated with the given short link from the database.

    Parameters:
        session (AsyncSession): The async session to interact with the database.
        short_link (str): The short link to search for in the database.

    Returns:
        Union[str, None]: The original link corresponding to the short link if found, otherwise None.
    """
    link = await session.scalar(select(Link).where(Link.short_link == short_link))
    return link


async def get_link_by_access_key(session: AsyncSession, access_key: str) -> Link | None:
    return await session.scalar(select(Link).where(Link.access_key == access_key))

async def create_transition(session: AsyncSession, link: Link,
                            from_ip: str, from_country: str, from_city: str,
                            to_ip: str, to_country: str, to_city: str,
                            forwarded_from: str) -> None:
    transition = Transition(link=link, from_ip=from_ip, from_country=from_country,
                             from_city=from_city, to_ip=to_ip, to_country=to_country,
                             to_city=to_city, forwarded_from=forwarded_from)
    session.add(transition)
    await session.commit()

async def get_link_stats_data(session: AsyncSession, link: Link) -> dict:  
    total_transitions = (await session.execute(
        select(func.count(Transition.id)).where(Transition.link_id == link.id)
    )).first()

    country_counts = (await session.execute(
        select(Transition.from_country, func.count(Transition.id))
        .where(Transition.link_id == link.id)
        .group_by(Transition.from_country)
    )).all()

    transitions_from_sites = (await session.execute(
        select(func.count(Transition.id)).where(Transition.forwarded_from != None))
    ).first()

    statistics = {
        "number_of_transitions": total_transitions[0],
        "number_of_transitions_by_country": 
        {country or "Undefined Country": count for country, count in country_counts},
        "number_of_transitions_from_sites": transitions_from_sites[0]
    }
    
    return statistics

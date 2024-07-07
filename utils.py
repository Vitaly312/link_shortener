from sqlalchemy.ext.asyncio import AsyncSession
import aiohttp
import socket
from database.crud import create_transition
from database.models import Link
from urllib.parse import urlparse


async def get_ip_info(ip: str) -> tuple[str]:
    """
    Asynchronously retrieves IP information from the ipapi.co API for a given IP address.

    Args:
        ip (str): The IP address to retrieve information for.

    Returns:
        dict[str]: A dictionary containing the country and city information for the given IP address.
                   The dictionary has the following keys:
                   - "country" (str): The country associated with the IP address.
                   - "city" (str): The city associated with the IP address.

    Raises:
        aiohttp.ClientError: If there was an error making the HTTP request.
        aiohttp.ClientResponseError: If the HTTP response was unsuccessful (status code 400-599).
        aiohttp.ClientPayloadError: If the HTTP response payload was invalid.
        json.JSONDecodeError: If the HTTP response payload could not be decoded as JSON.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://ipapi.co/{ip}/json/") as response:
            data: dict[str, str] = await response.json()
            return data.get('country'), data.get('city')
            

async def save_transition_info(session: AsyncSession, link: Link, from_ip: str,
                                http_referer: str = None):
    """
    Saves the transition information for a given link.

    Args:
        session (AsyncSession): The async session to interact with the database.
        link (Link): The link for which the transition information is being saved.
        from_ip (str): The IP address of the client making the request.
        http_referer (str, optional): The HTTP referer header value. Defaults to None.

    Returns:
        None

    This function retrieves the IP information for the `from_ip` using the `get_ip_info` function.
    It then retrieves the IP information for the `to_ip` if it is not None. If `to_ip` is None, the
    `to_country` and `to_city` values are set to None. The transition
    information is then saved in the database using the `create_transition` function.

    Note: This function assumes that the `get_ip_info` and `create_transition` functions are defined
    elsewhere in the codebase.
    """
    to_ip = socket.gethostbyname(urlparse(link.original_link).netloc)
    from_country, from_city = await get_ip_info(ip=from_ip)
    to_country, to_city = await get_ip_info(ip=to_ip) if to_ip else (None, None)
    
    await create_transition(session=session, link=link, from_ip=from_ip,
                            from_country=from_country, from_city=from_city,
                            to_ip=to_ip, to_country=to_country, to_city=to_city,
                            forwarded_from=http_referer)
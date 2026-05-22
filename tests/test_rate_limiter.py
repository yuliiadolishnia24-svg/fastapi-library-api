import pytest
from fastapi import Request, HTTPException
from unittest.mock import AsyncMock, MagicMock
from services.rate_limiter import check_rate_limit

def create_mock_request(host="127.0.0.1"):
    request = MagicMock(spec=Request)
    request.client = MagicMock()
    request.client.host = host
    return request

@pytest.mark.asyncio
async def test_anonymous_under_limit(mocker):
    mock_zrem = mocker.patch("services.rate_limiter.redis_client.zremrangebyscore", new_callable=AsyncMock)
    mock_zcard = mocker.patch("services.rate_limiter.redis_client.zcard", new_callable=AsyncMock, return_value=1)
    mock_zadd = mocker.patch("services.rate_limiter.redis_client.zadd", new_callable=AsyncMock)
    mock_expire = mocker.patch("services.rate_limiter.redis_client.expire", new_callable=AsyncMock)
    
    request = create_mock_request()
    await check_rate_limit(request, user_id=None)
    
    mock_zcard.assert_called_once()
    mock_zadd.assert_called_once()
    mock_expire.assert_called_once()

@pytest.mark.asyncio
async def test_anonymous_over_limit(mocker):
    mocker.patch("services.rate_limiter.redis_client.zremrangebyscore", new_callable=AsyncMock)
    mocker.patch("services.rate_limiter.redis_client.zcard", new_callable=AsyncMock, return_value=2)
    mock_expire = mocker.patch("services.rate_limiter.redis_client.expire", new_callable=AsyncMock)
    
    request = create_mock_request()
    
    with pytest.raises(HTTPException) as exc_info:
        await check_rate_limit(request, user_id=None)
        
    assert exc_info.value.status_code == 429

@pytest.mark.asyncio
async def test_authenticated_under_limit(mocker):
    mocker.patch("services.rate_limiter.redis_client.zremrangebyscore", new_callable=AsyncMock)
    mocker.patch("services.rate_limiter.redis_client.zcard", new_callable=AsyncMock, return_value=5)
    mock_zadd = mocker.patch("services.rate_limiter.redis_client.zadd", new_callable=AsyncMock)
    # КРИТИЧНИЙ МОК, ЯКОГО НЕ ВИСТАЧАЛО:
    mock_expire = mocker.patch("services.rate_limiter.redis_client.expire", new_callable=AsyncMock)
    
    request = create_mock_request()
    await check_rate_limit(request, user_id="user_12345")
    
    mock_zadd.assert_called_once()
    mock_expire.assert_called_once()

@pytest.mark.asyncio
async def test_authenticated_over_limit(mocker):
    mocker.patch("services.rate_limiter.redis_client.zremrangebyscore", new_callable=AsyncMock)
    mocker.patch("services.rate_limiter.redis_client.zcard", new_callable=AsyncMock, return_value=10)
    mock_expire = mocker.patch("services.rate_limiter.redis_client.expire", new_callable=AsyncMock)
    
    request = create_mock_request()
    
    with pytest.raises(HTTPException) as exc_info:
        await check_rate_limit(request, user_id="user_12345")
        
    assert exc_info.value.status_code == 429
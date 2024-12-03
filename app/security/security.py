"""
보안 관련 기능을 제공하는 모듈입니다.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import secrets
from pathlib import Path

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 보안 설정
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    """토큰 정보를 위한 모델"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """토큰 데이터를 위한 모델"""
    username: Optional[str] = None
    scopes: List[str] = []

class User(BaseModel):
    """사용자 정보를 위한 모델"""
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    scopes: List[str] = []

class UserInDB(User):
    """데이터베이스의 사용자 정보를 위한 모델"""
    hashed_password: str

class SecurityConfig:
    """보안 설정을 위한 클래스"""
    
    def __init__(self, secret_key: str):
        """
        Args:
            secret_key: JWT 토큰 생성에 사용할 시크릿 키
        """
        self.secret_key = secret_key
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.oauth2_scheme = OAuth2PasswordBearer(
            tokenUrl="token",
            scopes={
                "read": "Read access",
                "write": "Write access",
                "admin": "Admin access"
            }
        )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """비밀번호를 검증합니다.

        Args:
            plain_password: 평문 비밀번호
            hashed_password: 해시된 비밀번호

        Returns:
            비밀번호 일치 여부
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """비밀번호를 해시화합니다.

        Args:
            password: 평문 비밀번호

        Returns:
            해시된 비밀번호
        """
        return self.pwd_context.hash(password)

    def create_access_token(
        self,
        data: Dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """접근 토큰을 생성합니다.

        Args:
            data: 토큰에 포함할 데이터
            expires_delta: 토큰 만료 시간

        Returns:
            생성된 JWT 토큰
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=ALGORITHM
        )
        return encoded_jwt

    async def get_current_user(
        self,
        token: str = Depends(oauth2_scheme)
    ) -> User:
        """현재 사용자 정보를 가져옵니다.

        Args:
            token: JWT 토큰

        Returns:
            현재 사용자 정보

        Raises:
            HTTPException: 인증 실패 시
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[ALGORITHM]
            )
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            
            token_scopes = payload.get("scopes", [])
            token_data = TokenData(username=username, scopes=token_scopes)
        
        except JWTError:
            raise credentials_exception
        
        user = self.get_user(username=token_data.username)
        if user is None:
            raise credentials_exception
        
        return user

    async def get_current_active_user(
        self,
        current_user: User = Depends(get_current_user)
    ) -> User:
        """현재 활성 사용자 정보를 가져옵니다.

        Args:
            current_user: 현재 사용자 정보

        Returns:
            현재 활성 사용자 정보

        Raises:
            HTTPException: 사용자가 비활성화된 경우
        """
        if current_user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user

class DataEncryption:
    """데이터 암호화를 위한 클래스"""

    def __init__(self, key_path: Union[str, Path]):
        """
        Args:
            key_path: 암호화 키 파일 경로
        """
        self.key_path = Path(key_path)
        self._load_or_generate_key()

    def _load_or_generate_key(self) -> None:
        """암호화 키를 로드하거나 생성합니다."""
        try:
            if self.key_path.exists():
                with open(self.key_path, 'rb') as f:
                    self.key = f.read()
            else:
                self.key = secrets.token_bytes(32)
                self.key_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.key_path, 'wb') as f:
                    f.write(self.key)
        except Exception as e:
            logger.error(f"Failed to load or generate key: {e}")
            raise

    def encrypt_data(self, data: bytes) -> bytes:
        """데이터를 암호화합니다.

        Args:
            data: 암호화할 데이터

        Returns:
            암호화된 데이터
        """
        from cryptography.fernet import Fernet
        f = Fernet(self.key)
        return f.encrypt(data)

    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """데이터를 복호화합니다.

        Args:
            encrypted_data: 복호화할 데이터

        Returns:
            복호화된 데이터
        """
        from cryptography.fernet import Fernet
        f = Fernet(self.key)
        return f.decrypt(encrypted_data)

class APIKeyManager:
    """API 키 관리를 위한 클래스"""

    def __init__(self, keys_file: Union[str, Path]):
        """
        Args:
            keys_file: API 키 정보를 저장할 파일 경로
        """
        self.keys_file = Path(keys_file)
        self._load_keys()

    def _load_keys(self) -> None:
        """저장된 API 키를 로드합니다."""
        try:
            if self.keys_file.exists():
                with open(self.keys_file, 'r') as f:
                    self.api_keys = json.load(f)
            else:
                self.api_keys = {}
        except Exception as e:
            logger.error(f"Failed to load API keys: {e}")
            self.api_keys = {}

    def generate_api_key(self, user_id: str, scopes: List[str]) -> str:
        """새로운 API 키를 생성합니다.

        Args:
            user_id: 사용자 ID
            scopes: API 키의 권한 범위

        Returns:
            생성된 API 키
        """
        api_key = secrets.token_urlsafe(32)
        self.api_keys[api_key] = {
            'user_id': user_id,
            'scopes': scopes,
            'created_at': datetime.now().isoformat()
        }
        self._save_keys()
        return api_key

    def validate_api_key(self, api_key: str, required_scope: str) -> bool:
        """API 키의 유효성을 검사합니다.

        Args:
            api_key: 검사할 API 키
            required_scope: 필요한 권한 범위

        Returns:
            API 키의 유효성 여부
        """
        key_info = self.api_keys.get(api_key)
        if not key_info:
            return False
        return required_scope in key_info['scopes']

    def revoke_api_key(self, api_key: str) -> None:
        """API 키를 폐기합니다.

        Args:
            api_key: 폐기할 API 키
        """
        if api_key in self.api_keys:
            del self.api_keys[api_key]
            self._save_keys()

    def _save_keys(self) -> None:
        """API 키 정보를 파일에 저장합니다."""
        try:
            self.keys_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.keys_file, 'w') as f:
                json.dump(self.api_keys, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save API keys: {e}")
            raise

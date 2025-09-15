#!/usr/bin/env python3
"""
Script para probar que todas las importaciones funcionan correctamente
"""


def test_imports():
    """Test all imports"""
    try:
        print("Testing imports...")

        # Test basic imports
        from app.config import settings

        assert settings is not None
        print("✅ Config import successful")

        from app.utils.logging import get_logger, setup_logging

        assert get_logger is not None
        assert setup_logging is not None
        print("✅ Logging import successful")

        from app.utils.rate_limiting import RateLimitMiddleware

        assert RateLimitMiddleware is not None
        print("✅ Rate limiting import successful")

        from app.api.health import router as health_router

        assert health_router is not None
        print("✅ Health router import successful")

        from app.api import api_router

        assert api_router is not None
        print("✅ API router import successful")

        from app.api.v1 import api_router as v1_router

        assert v1_router is not None
        print("✅ V1 router import successful")

        from app.api.v2 import api_router as v2_router

        assert v2_router is not None
        print("✅ V2 router import successful")

        from app.api.v2.auth import router as v2_auth_router

        assert v2_auth_router is not None
        print("✅ V2 auth router import successful")

        from app.api.v2.tasks import router as v2_tasks_router

        assert v2_tasks_router is not None
        print("✅ V2 tasks router import successful")

        print("\n🎉 All imports successful!")
        assert True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        assert False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        assert False


if __name__ == "__main__":
    test_imports()

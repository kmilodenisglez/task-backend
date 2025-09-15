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

        print("✅ Config import successful")

        from app.utils.logging import get_logger, setup_logging

        print("✅ Logging import successful")

        from app.utils.rate_limiting import RateLimitMiddleware

        print("✅ Rate limiting import successful")

        from app.api.health import router as health_router

        print("✅ Health router import successful")

        from app.api import api_router

        print("✅ API router import successful")

        from app.api.v1 import api_router as v1_router

        print("✅ V1 router import successful")

        from app.api.v2 import api_router as v2_router

        print("✅ V2 router import successful")

        from app.api.v2.auth import router as v2_auth_router

        print("✅ V2 auth router import successful")

        from app.api.v2.tasks import router as v2_tasks_router

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

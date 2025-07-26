#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Telegram Bot Implementation
Tests health check, webhook endpoint, bot functionality, and state management
"""

import requests
import json
import os
import sys
import time
from unittest.mock import Mock, patch

# Add backend to path
sys.path.append('/app/backend')

def test_health_check():
    """Test GET / endpoint returns correct status"""
    print("🔍 Testing Health Check Endpoint...")
    
    try:
        response = requests.get("http://localhost:8001/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "Menfes API Aktif":
                print("✅ Health check endpoint working correctly")
                return True
            else:
                print(f"❌ Health check returned wrong status: {data}")
                return False
        else:
            print(f"❌ Health check failed with status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server on port 8001")
        return False
    except Exception as e:
        print(f"❌ Health check test failed: {str(e)}")
        return False

def test_webhook_endpoint():
    """Test POST / endpoint can receive webhook updates"""
    print("\n🔍 Testing Webhook Endpoint...")
    
    # Mock Telegram update data
    mock_update = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 987654321,
                "is_bot": False,
                "first_name": "TestUser",
                "username": "testuser"
            },
            "chat": {
                "id": 987654321,
                "first_name": "TestUser",
                "username": "testuser",
                "type": "private"
            },
            "date": 1640995200,
            "text": "/start"
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/",
            json=mock_update,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok") == True:
                print("✅ Webhook endpoint accepting updates correctly")
                return True
            else:
                print(f"❌ Webhook returned unexpected response: {data}")
                return False
        else:
            print(f"❌ Webhook failed with status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to webhook endpoint")
        return False
    except Exception as e:
        print(f"❌ Webhook test failed: {str(e)}")
        return False

def test_bot_configuration():
    """Test bot configuration and environment variables"""
    print("\n🔍 Testing Bot Configuration...")
    
    try:
        # Import server module to check configuration
        import server
        
        # Check BOT_TOKEN is configured
        if hasattr(server, 'BOT_TOKEN') and server.BOT_TOKEN:
            print("✅ BOT_TOKEN is configured")
        else:
            print("❌ BOT_TOKEN is missing or empty")
            return False
            
        # Check CHANNEL_ID is configured
        if hasattr(server, 'CHANNEL_ID') and server.CHANNEL_ID == -1002589515039:
            print("✅ CHANNEL_ID is correctly configured")
        else:
            print("❌ CHANNEL_ID is missing or incorrect")
            return False
            
        # Check REQUIRED_CHATS
        expected_chats = ["@Anofes", "@Mwtlan", "@KhamahdalysRoom"]
        if hasattr(server, 'REQUIRED_CHATS') and server.REQUIRED_CHATS == expected_chats:
            print("✅ REQUIRED_CHATS are correctly configured")
        else:
            print("❌ REQUIRED_CHATS are missing or incorrect")
            return False
            
        # Check bot instance
        if hasattr(server, 'bot') and server.bot:
            print("✅ Bot instance is created")
        else:
            print("❌ Bot instance is missing")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Cannot import server module: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Bot configuration test failed: {str(e)}")
        return False

def test_state_management():
    """Test in-memory state storage functionality"""
    print("\n🔍 Testing State Management...")
    
    try:
        import server
        
        # Test state dictionary exists
        if hasattr(server, 'state') and isinstance(server.state, dict):
            print("✅ State dictionary is initialized")
        else:
            print("❌ State dictionary is missing or wrong type")
            return False
            
        # Test state operations
        test_user_id = 123456789
        
        # Test setting state
        server.state[test_user_id] = "choose_lang"
        if server.state.get(test_user_id) == "choose_lang":
            print("✅ State setting works correctly")
        else:
            print("❌ State setting failed")
            return False
            
        # Test updating state
        server.state[test_user_id] = "verifying"
        if server.state.get(test_user_id) == "verifying":
            print("✅ State updating works correctly")
        else:
            print("❌ State updating failed")
            return False
            
        # Test complex state (dict)
        server.state[test_user_id] = {"state": "preview", "text": "Test message"}
        stored_state = server.state.get(test_user_id)
        if isinstance(stored_state, dict) and stored_state.get("text") == "Test message":
            print("✅ Complex state storage works correctly")
        else:
            print("❌ Complex state storage failed")
            return False
            
        # Clean up test state
        del server.state[test_user_id]
        
        return True
        
    except Exception as e:
        print(f"❌ State management test failed: {str(e)}")
        return False

def test_bot_handlers():
    """Test bot handler functions exist and are properly configured"""
    print("\n🔍 Testing Bot Handlers...")
    
    try:
        import server
        
        # Check if bot handlers are registered
        if hasattr(server.bot, 'message_handlers') and server.bot.message_handlers:
            print("✅ Message handlers are registered")
        else:
            print("❌ No message handlers found")
            return False
            
        if hasattr(server.bot, 'callback_query_handlers') and server.bot.callback_query_handlers:
            print("✅ Callback query handlers are registered")
        else:
            print("❌ No callback query handlers found")
            return False
            
        # Test specific handler functions exist
        handler_functions = ['on_start', 'on_lang_selected', 'on_check_join', 
                           'on_message_received', 'on_edit', 'on_send']
        
        for func_name in handler_functions:
            if hasattr(server, func_name):
                print(f"✅ Handler function {func_name} exists")
            else:
                print(f"❌ Handler function {func_name} is missing")
                return False
                
        # Test utility functions
        if hasattr(server, 'join_buttons') and callable(server.join_buttons):
            print("✅ join_buttons utility function exists")
        else:
            print("❌ join_buttons utility function is missing")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Bot handlers test failed: {str(e)}")
        return False

def test_dependencies():
    """Test that all required dependencies are available"""
    print("\n🔍 Testing Dependencies...")
    
    required_modules = ['fastapi', 'telebot', 'uvicorn']
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} is available")
        except ImportError:
            print(f"❌ {module} is missing")
            return False
            
    return True

def test_fastapi_app():
    """Test FastAPI application configuration"""
    print("\n🔍 Testing FastAPI Application...")
    
    try:
        import server
        
        # Check FastAPI app exists
        if hasattr(server, 'app') and server.app:
            print("✅ FastAPI app instance exists")
        else:
            print("❌ FastAPI app instance is missing")
            return False
            
        # Check routes are configured
        routes = [route.path for route in server.app.routes]
        
        if "/" in routes:
            print("✅ Root route is configured")
        else:
            print("❌ Root route is missing")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ FastAPI app test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all backend tests and return overall result"""
    print("🚀 Starting Comprehensive Backend Testing for Telegram Bot\n")
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Bot Configuration", test_bot_configuration),
        ("FastAPI Application", test_fastapi_app),
        ("State Management", test_state_management),
        ("Bot Handlers", test_bot_handlers),
        ("Health Check Endpoint", test_health_check),
        ("Webhook Endpoint", test_webhook_endpoint)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results[test_name] = False
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print("="*60)
    print(f"Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All backend tests PASSED! System is ready for deployment.")
        return True
    else:
        print("⚠️  Some tests FAILED. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
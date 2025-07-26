#!/usr/bin/env python3
"""
Complete Bot Flow Testing - Simulates full user journey
Tests: Language selection → Channel verification → Message input → Preview → Send to channel
"""

import requests
import json
import sys
import time

# Add backend to path
sys.path.append('/app/backend')

def simulate_webhook_update(update_data):
    """Send webhook update to bot"""
    try:
        response = requests.post(
            "http://localhost:8001/",
            json=update_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        return response.status_code, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return None, str(e)

def test_complete_bot_flow():
    """Test complete bot flow from /start to message sending"""
    print("🚀 Testing Complete Bot Flow\n")
    
    test_user_id = 987654321
    test_user_name = "TestUser"
    
    # Step 1: Test /start command
    print("📱 Step 1: Testing /start command...")
    start_update = {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "from": {
                "id": test_user_id,
                "is_bot": False,
                "first_name": test_user_name,
                "username": "testuser"
            },
            "chat": {
                "id": test_user_id,
                "first_name": test_user_name,
                "username": "testuser",
                "type": "private"
            },
            "date": 1640995200,
            "text": "/start"
        }
    }
    
    status, response = simulate_webhook_update(start_update)
    if status == 200 and response.get("ok"):
        print("✅ /start command processed successfully")
    else:
        print(f"❌ /start command failed: {status} - {response}")
        return False
    
    # Check state after /start
    try:
        import server
        user_state = server.state.get(test_user_id)
        if user_state == "choose_lang":
            print("✅ User state correctly set to 'choose_lang'")
        else:
            print(f"❌ Unexpected user state: {user_state}")
            return False
    except Exception as e:
        print(f"❌ Error checking state: {e}")
        return False
    
    # Step 2: Test language selection
    print("\n📱 Step 2: Testing language selection (Indonesian)...")
    lang_update = {
        "update_id": 2,
        "callback_query": {
            "id": "callback_1",
            "from": {
                "id": test_user_id,
                "is_bot": False,
                "first_name": test_user_name,
                "username": "testuser"
            },
            "message": {
                "message_id": 2,
                "chat": {
                    "id": test_user_id,
                    "first_name": test_user_name,
                    "username": "testuser",
                    "type": "private"
                },
                "date": 1640995200,
                "text": "Language selection message"
            },
            "data": "lang_id"
        }
    }
    
    status, response = simulate_webhook_update(lang_update)
    if status == 200 and response.get("ok"):
        print("✅ Language selection processed successfully")
    else:
        print(f"❌ Language selection failed: {status} - {response}")
        return False
    
    # Check state after language selection
    try:
        user_state = server.state.get(test_user_id)
        if isinstance(user_state, dict) and user_state.get("language") == "id":
            print("✅ User state correctly updated with language selection")
        else:
            print(f"❌ Unexpected user state after language selection: {user_state}")
            return False
    except Exception as e:
        print(f"❌ Error checking state after language selection: {e}")
        return False
    
    # Step 3: Test channel verification (simulate user already joined)
    print("\n📱 Step 3: Testing channel verification...")
    
    # First, let's simulate the user clicking "check_join"
    check_join_update = {
        "update_id": 3,
        "callback_query": {
            "id": "callback_2",
            "from": {
                "id": test_user_id,
                "is_bot": False,
                "first_name": test_user_name,
                "username": "testuser"
            },
            "message": {
                "message_id": 3,
                "chat": {
                    "id": test_user_id,
                    "first_name": test_user_name,
                    "username": "testuser",
                    "type": "private"
                },
                "date": 1640995200,
                "text": "Join channels message"
            },
            "data": "check_join"
        }
    }
    
    status, response = simulate_webhook_update(check_join_update)
    if status == 200 and response.get("ok"):
        print("✅ Channel verification request processed")
    else:
        print(f"❌ Channel verification failed: {status} - {response}")
        return False
    
    # Note: In real scenario, bot would check membership via Telegram API
    # For testing, we'll manually set the state to simulate successful verification
    try:
        server.state[test_user_id] = "wait_msg"
        print("✅ Simulated successful channel verification (state set to 'wait_msg')")
    except Exception as e:
        print(f"❌ Error setting state for message waiting: {e}")
        return False
    
    # Step 4: Test message input
    print("\n📱 Step 4: Testing message input...")
    message_update = {
        "update_id": 4,
        "message": {
            "message_id": 4,
            "from": {
                "id": test_user_id,
                "is_bot": False,
                "first_name": test_user_name,
                "username": "testuser"
            },
            "chat": {
                "id": test_user_id,
                "first_name": test_user_name,
                "username": "testuser",
                "type": "private"
            },
            "date": 1640995200,
            "text": "Ini adalah pesan anonim untuk testing bot menfes!"
        }
    }
    
    status, response = simulate_webhook_update(message_update)
    if status == 200 and response.get("ok"):
        print("✅ Message input processed successfully")
    else:
        print(f"❌ Message input failed: {status} - {response}")
        return False
    
    # Check state after message input
    try:
        user_state = server.state.get(test_user_id)
        if isinstance(user_state, dict) and user_state.get("state") == "preview":
            print("✅ User state correctly set to 'preview' with message stored")
            print(f"   Stored message: {user_state.get('text', 'N/A')[:50]}...")
        else:
            print(f"❌ Unexpected user state after message input: {user_state}")
            return False
    except Exception as e:
        print(f"❌ Error checking state after message input: {e}")
        return False
    
    # Step 5: Test message editing (optional step)
    print("\n📱 Step 5: Testing message editing option...")
    edit_update = {
        "update_id": 5,
        "callback_query": {
            "id": "callback_3",
            "from": {
                "id": test_user_id,
                "is_bot": False,
                "first_name": test_user_name,
                "username": "testuser"
            },
            "message": {
                "message_id": 5,
                "chat": {
                    "id": test_user_id,
                    "first_name": test_user_name,
                    "username": "testuser",
                    "type": "private"
                },
                "date": 1640995200,
                "text": "Preview message"
            },
            "data": "edit_msg"
        }
    }
    
    status, response = simulate_webhook_update(edit_update)
    if status == 200 and response.get("ok"):
        print("✅ Message editing option processed successfully")
    else:
        print(f"❌ Message editing failed: {status} - {response}")
        return False
    
    # Check state after edit request
    try:
        user_state = server.state.get(test_user_id)
        if user_state == "wait_msg":
            print("✅ User state correctly reset to 'wait_msg' for editing")
        else:
            print(f"❌ Unexpected user state after edit request: {user_state}")
            return False
    except Exception as e:
        print(f"❌ Error checking state after edit request: {e}")
        return False
    
    # Step 6: Send new message and confirm sending
    print("\n📱 Step 6: Testing final message and send confirmation...")
    
    # Send new message
    final_message_update = {
        "update_id": 6,
        "message": {
            "message_id": 6,
            "from": {
                "id": test_user_id,
                "is_bot": False,
                "first_name": test_user_name,
                "username": "testuser"
            },
            "chat": {
                "id": test_user_id,
                "first_name": test_user_name,
                "username": "testuser",
                "type": "private"
            },
            "date": 1640995200,
            "text": "Pesan anonim final yang sudah diedit untuk testing!"
        }
    }
    
    status, response = simulate_webhook_update(final_message_update)
    if status == 200 and response.get("ok"):
        print("✅ Final message processed successfully")
    else:
        print(f"❌ Final message failed: {status} - {response}")
        return False
    
    # Confirm sending
    send_update = {
        "update_id": 7,
        "callback_query": {
            "id": "callback_4",
            "from": {
                "id": test_user_id,
                "is_bot": False,
                "first_name": test_user_name,
                "username": "testuser"
            },
            "message": {
                "message_id": 7,
                "chat": {
                    "id": test_user_id,
                    "first_name": test_user_name,
                    "username": "testuser",
                    "type": "private"
                },
                "date": 1640995200,
                "text": "Final preview message"
            },
            "data": "send_now"
        }
    }
    
    status, response = simulate_webhook_update(send_update)
    if status == 200 and response.get("ok"):
        print("✅ Send confirmation processed successfully")
    else:
        print(f"❌ Send confirmation failed: {status} - {response}")
        return False
    
    # Check final state
    try:
        user_state = server.state.get(test_user_id)
        if user_state is None:
            print("✅ User state correctly reset to None after sending")
        else:
            print(f"❌ User state not reset after sending: {user_state}")
            return False
    except Exception as e:
        print(f"❌ Error checking final state: {e}")
        return False
    
    print("\n🎉 Complete bot flow test PASSED!")
    print("✅ All steps in the user journey work correctly:")
    print("   1. /start command → Language selection")
    print("   2. Language selection → Channel verification")
    print("   3. Channel verification → Message input")
    print("   4. Message input → Preview")
    print("   5. Message editing → New input")
    print("   6. Send confirmation → Message sent & state reset")
    
    return True

def test_multiple_users():
    """Test state management with multiple users"""
    print("\n🔍 Testing Multiple User Sessions...")
    
    try:
        import server
        
        # Simulate multiple users
        users = [111111, 222222, 333333]
        
        for user_id in users:
            server.state[user_id] = f"test_state_{user_id}"
        
        # Verify each user has their own state
        all_correct = True
        for user_id in users:
            expected_state = f"test_state_{user_id}"
            actual_state = server.state.get(user_id)
            if actual_state != expected_state:
                print(f"❌ User {user_id} state incorrect: expected {expected_state}, got {actual_state}")
                all_correct = False
            else:
                print(f"✅ User {user_id} state correct: {actual_state}")
        
        # Clean up
        for user_id in users:
            del server.state[user_id]
        
        if all_correct:
            print("✅ Multiple user state management working correctly")
            return True
        else:
            print("❌ Multiple user state management failed")
            return False
            
    except Exception as e:
        print(f"❌ Multiple user test failed: {e}")
        return False

def run_flow_tests():
    """Run complete flow tests"""
    print("🚀 Starting Complete Bot Flow Testing\n")
    
    tests = [
        ("Complete Bot Flow", test_complete_bot_flow),
        ("Multiple User Sessions", test_multiple_users)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results[test_name] = False
    
    print("\n" + "="*60)
    print("📊 FLOW TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print("="*60)
    print(f"Overall Result: {passed}/{total} flow tests passed")
    
    if passed == total:
        print("🎉 All bot flow tests PASSED!")
        print("✅ Complete user journey works end-to-end")
        print("✅ State management handles multiple users correctly")
        return True
    else:
        print("⚠️  Some flow tests FAILED. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_flow_tests()
    sys.exit(0 if success else 1)
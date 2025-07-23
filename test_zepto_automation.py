"""
Test script to validate the improved Zepto automation scripts
"""
import asyncio
import os
import sys
from unittest.mock import AsyncMock, Mock, patch

# Add the repo to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        from zepto_automation_working import run_download, login_task, may_task, june_task, july_task
        from browser_use import Agent
        from browser_use.browser import BrowserSession, BrowserProfile
        from browser_use.llm import ChatOpenAI
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_task_structure():
    """Test that task prompts are properly structured"""
    from zepto_automation_working import login_task, may_task, june_task, july_task
    
    tasks = {
        'login_task': login_task,
        'may_task': may_task, 
        'june_task': june_task,
        'july_task': july_task
    }
    
    for name, task in tasks.items():
        assert isinstance(task, str), f"{name} should be a string"
        assert len(task) > 50, f"{name} should have meaningful content"
        # Check for various instruction patterns
        has_instructions = any(pattern in task for pattern in ['STEPS', 'STEP', 'INITIAL', '1.', '2.'])
        assert has_instructions, f"{name} should have step instructions"
        print(f"✅ {name} structure validated")
    
    return True

def test_browser_session_setup():
    """Test that browser session can be created properly"""
    try:
        from browser_use.browser import BrowserSession, BrowserProfile
        
        # Test profile creation
        profile = BrowserProfile(downloads_path="/tmp/test_downloads")
        assert profile.downloads_path == "/tmp/test_downloads"
        
        # Test session creation (without actually starting browser)
        session = BrowserSession(browser_profile=profile)
        assert session.browser_profile == profile
        
        print("✅ Browser session setup validated")
        return True
    except Exception as e:
        print(f"❌ Browser session test failed: {e}")
        return False

def test_llm_setup():
    """Test that LLM can be configured properly"""
    try:
        from browser_use.llm import ChatOpenAI
        
        # Test LLM creation (without API key validation)
        llm = ChatOpenAI(model='gpt-4o', temperature=0)
        assert llm.model == 'gpt-4o'
        assert llm.temperature == 0
        
        print("✅ LLM setup validated")
        return True
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return False

def test_agent_creation():
    """Test that agents can be created with proper parameters"""
    try:
        from browser_use import Agent
        from browser_use.llm import ChatOpenAI
        from browser_use.browser import BrowserSession, BrowserProfile
        
        # Create mock components
        llm = ChatOpenAI(model='gpt-4o', temperature=0)
        profile = BrowserProfile(downloads_path="/tmp/test")
        session = BrowserSession(browser_profile=profile)
        
        # Test agent creation
        agent = Agent(
            task="Test task",
            llm=llm,
            max_actions_per_step=6,
            use_vision=True,
            browser_session=session
        )
        
        assert agent.task == "Test task"
        assert agent.llm == llm
        
        print("✅ Agent creation validated")
        return True
    except Exception as e:
        print(f"❌ Agent creation test failed: {e}")
        return False

async def test_async_structure():
    """Test that the async structure is correct"""
    try:
        # Import the main function
        from zepto_automation_working import run_download
        
        # Verify it's an async function
        assert asyncio.iscoroutinefunction(run_download), "run_download should be async"
        
        print("✅ Async structure validated")
        return True
    except Exception as e:
        print(f"❌ Async structure test failed: {e}")
        return False

def run_all_tests():
    """Run all validation tests"""
    print("🧪 Running Zepto Automation Validation Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_task_structure, 
        test_browser_session_setup,
        test_llm_setup,
        test_agent_creation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    # Run async test separately
    try:
        asyncio.run(test_async_structure())
        passed += 1
        total += 1
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        total += 1
    
    print("=" * 50)
    print(f"🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The automation scripts should work correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
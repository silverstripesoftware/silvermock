#
#  Copyright (c) 2007 Silver Stripe Software Pvt Ltd
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.
#
#
#  Contributions and bug reports are welcome. Send an email to
#  siddharta at silverstripesoftware dot com
#

def patch_function(function, classNameList, newClassList):
    """This function allows us to substitute a class used by a function with
    a mock class"""

    def _patched_function(*args):
        oldClassList = []
        for oldClassName, newClass in zip(classNameList, newClassList):
            oldClassList.append(function.func_globals[oldClassName])
            function.func_globals[oldClassName] = newClass
        try:
            return_value = function(*args)
        finally:
            for oldClassName, oldClass in zip(classNameList, oldClassList):
                function.func_globals[oldClassName] = oldClass
        return return_value
    return _patched_function

class MockVerificationFailure(Exception):
    """Thrown when there is a mock verification failure"""
    pass

class OfType(object):
    """Test the type of a parameter instead of the value"""

    def __init__(self, type):
        self.type = type
        
    def __eq__(self, x):
        return (type(x) == self.type) or (isinstance(x, self.type))

    def __repr__(self):
        return self.__unicode__()

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return str(self.type)

class Call(object):
    """This class represents a function call"""
    
    def __init__(self, functionName, args=None, retval=None, execute=None):
        self.function = functionName
        self.args = ()
        if args:
            self.args = args
        self.retval = retval
        self.execute = lambda args: None
        if execute:
            self.execute = execute

    def with_args(self, args):
        self.args = args
        return self

    def and_return(self, retval):
        self.retval = retval
        return self
    
    def and_execute(self, execute):
        self.execute = execute
        return self

    def execute_value(self):
        return self.execute

    def return_value(self):
        return self.retval

    def __cmp__(self, x):
        if self.compare_function(x) and self.compare_arguments(x):
            return 0
        return -1

    def compare_function(self, x):
        if self.function != x.function:
            return False
        return True
    
    def compare_arguments(self, x):
        if len(self.args) != len(x.args):
            return False
        for i, arg in enumerate(self.args):
            if not arg == x.args[i]:
                return False
        return True

    def __repr__(self):
        return self.__unicode__()

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.function

ShouldBeCalled = Call

class MockObject(object):
    """This class creates a mock object class configured with the expectation list
    and returns the mock object class"""

    def __new__(cls, name="MockObject", call_list=[]):
        class _MockObject(object):
            def __init__(self, *args):
                self.__class__._instance = self
                self.actual_list.append(Call("__init__", args))
                call_count = len(self.actual_list)
                call = self.actual_list[0]
                if call_count - 1 < len(self.expected_list):
                    expected = self.expected_list[0]
                    if expected == call:
                        expected.execute_value()(args)

            def _mock_function(self, *args):
                call_count = len(self.actual_list)
                call = self.actual_list[-1]
                call.with_args(args)
                if call_count - 1 < len(self.expected_list):
                    expected = self.expected_list[call_count - 1]
                    if expected == call:
                        expected.execute_value()(args)
                        return expected.return_value()

            def _log_call(self, name, args=()):
                self.actual_list.append(Call(name, args))
                return self._mock_function

            def verify(self):
                """This is the only method that is called outside the constructor and is used to verify
                that the calls were made correctly to the mock object"""

                i = 0
                while (i < len(self.expected_list)) and (i < len(self.actual_list)):
                    if not self.expected_list[i].compare_function(self.actual_list[i]):
                        raise MockVerificationFailure("Call Mismatch: Expected <%s>, Was <%s>" % (self.expected_list[i], self.actual_list[i]))
                    if not self.expected_list[i].compare_arguments(self.actual_list[i]):
                        raise MockVerificationFailure("Argument Mismatch: Expected <%s>, Was <%s>" % (self.expected_list[i].args, self.actual_list[i].args))
                    i += 1
                if i < len(self.expected_list):
                    raise MockVerificationFailure("Not Called: <%s>" % (self.expected_list[i]))
                if i < len(self.actual_list):
                    raise MockVerificationFailure("Surprise: <%s>" % (self.actual_list[i]))

            def __iter__(self):
                return self._log_call("__iter__")()

            def __getattr__(self, name):
                return self._log_call(name)

            def __repr__(self):
                return self.__unicode__()

            def __str__(self):
                return self.__unicode__()
            
            def __unicode__(self):
                return self.name

        _MockObject.name = name
        _MockObject._instance = None
        _MockObject.expected_list = call_list
        _MockObject.actual_list = []
        return _MockObject

#
#  Unit tests. Run this file on the command line to run the tests
#

import unittest

class DummyClass1(object):
    pass

class DummyClass2(object):
    pass

class DummyClass3(object):
    pass

class PatchFunctionTest(unittest.TestCase):
    def testPatchedFunctionHasClassReplaced(self):
        """Patch the function and replace DummyClass1 & DummyClass2 with DummyClass3. 
        When the patched function is executed, it should return DummyClass3, DummyClass3"""

        def function_to_patch():
            return DummyClass1, DummyClass2

        patched_function = patch_function(function_to_patch, ["DummyClass1", "DummyClass2"], [DummyClass3, DummyClass3])
        class1, class2 = patched_function()
        self.assertEquals(DummyClass3, class1)
        self.assertEquals(DummyClass3, class2)

class OfTypeTest(unittest.TestCase):
    def testTypeEqualityForTypes(self):
        self.assertTrue(OfType(int).__eq__(5))
        self.assertTrue(OfType(int) == 5)
        self.assertTrue(5 == OfType(int))
        self.assertTrue(OfType(type(10)) == 5)
        self.assertTrue(5 == OfType(type(10)))

    def testTypeEqualityForClasses(self):
        class A(object):
            pass
        
        self.assertTrue(OfType(A) == A())
        self.assertTrue(A() == OfType(A))
        
    def testTypeEqualityForInheritedClasses(self):
        class A(object):
            pass
        
        class B(A):
            pass
        
        self.assertTrue(OfType(A) == B())
        self.assertTrue(OfType(B) == B())
        self.assertTrue(B() == OfType(A))
        self.assertTrue(B() == OfType(B))

class CallTest(unittest.TestCase):
    def testCallDefaultInit(self):
        call = Call("function")
        self.assertEquals("function", call.function)
        self.assertEquals((), call.args)
        self.assertEquals(None, call.execute(()))
        self.assertEquals(None, call.retval)

    def testCallFullInit(self):
        fn = lambda args: 1
        call = Call("function", args=(1,2,3), retval=True, execute=fn)
        self.assertEquals("function", call.function)
        self.assertEquals((1,2,3), call.args)
        self.assertEquals(fn, call.execute)
        self.assertEquals(True, call.retval)

    def testWithArgs(self):
        call = Call("function")
        self.assertEquals(call, call.with_args((1,2,3)))
        self.assertEquals((1,2,3), call.args)

    def testAndReturn(self):
        call = Call("function")
        self.assertEquals(call, call.and_return(True))
        self.assertEquals(True, call.retval)
        self.assertEquals(True, call.return_value())

    def testAndExecute(self):
        fn = lambda args: 1
        call = Call("function")
        self.assertEquals(call, call.and_execute(fn))
        self.assertEquals(fn, call.execute)
        self.assertEquals(fn, call.execute_value())

    def testCompareByFunctionName(self):
        call1 = Call("function")
        call2 = Call("function")
        call3 = Call("fn")

        self.assertEquals(call1, call2)
        self.assertNotEquals(call1, call3)
        
    def testCompareByArguments(self):
        call1 = Call("function", args=(1,2,3))
        call2 = Call("function", args=(1,2,3))
        call3 = Call("function", args=(1,2,4))
        call4 = Call("function", args=(1,2))
        call5 = Call("function", args=(1,2,3,4))

        self.assertEquals(call1, call2)
        self.assertNotEquals(call1, call3)
        self.assertNotEquals(call1, call4)
        self.assertNotEquals(call1, call5)

    def testCompareWithIndirectArguments(self):
        call1 = Call("function", args=(1,"",[]))
        call2 = Call("function", args=(OfType(int),OfType(str),OfType(list)))
        call3 = Call("function", args=(1,"",3))

        self.assertEquals(call1, call2)
        self.assertNotEquals(call1, call3)

class MockObjectTest(unittest.TestCase):
    def testMockObjectInit(self):
        mock = MockObject("mock class", [1,2,3])
        self.assertEquals("mock class", mock.name)
        self.assertEquals(None, mock._instance)
        self.assertEquals([1,2,3], mock.expected_list)
        self.assertEquals([], mock.actual_list)

    def testSuccessfulVerify(self):
        mock = MockObject("mock class", [
            ShouldBeCalled("__init__"),
            ShouldBeCalled("function")
        ])
        obj = mock()
        obj.function()
        
        mock._instance.verify()

    def testSuccessfulVerifyWithArguments(self):
        mock = MockObject("mock class", [
            ShouldBeCalled("__init__"),
            ShouldBeCalled("function").with_args((1,2))
        ])
        obj = mock()
        obj.function(1,2)
        
        mock._instance.verify()

    def testReturnValue(self):
        mock = MockObject("mock class", [
            ShouldBeCalled("__init__"),
            ShouldBeCalled("function").and_return(True)
        ])
        obj = mock()
        self.assertTrue(obj.function())

    def testExecute(self):
        class execution(object):
            def fn(self, args):
                self.x = args

        e = execution()
        mock = MockObject("mock class", [
            ShouldBeCalled("__init__"),
            ShouldBeCalled("function").with_args((1,2,3)).and_execute(e.fn)
        ])
        obj = mock()
        obj.function(1,2,3)
        
        self.assertEquals((1,2,3), e.x)

    def testWrongFunction(self):
        mock = MockObject("mock class", [
            ShouldBeCalled("__init__"),
            ShouldBeCalled("function")
        ])
        obj = mock()
        obj.wrong_function()
        
        self.assertRaises(MockVerificationFailure, mock._instance.verify)

    def testFunctionNotCalled(self):
        mock = MockObject("mock class", [
            ShouldBeCalled("__init__"),
            ShouldBeCalled("function")
        ])
        obj = mock()
        
        self.assertRaises(MockVerificationFailure, mock._instance.verify)

    def testFunctionSurpriseCall(self):
        mock = MockObject("mock class", [
            ShouldBeCalled("__init__"),
        ])
        obj = mock()
        obj.function()
        
        self.assertRaises(MockVerificationFailure, mock._instance.verify)

    def testArgumentMismatch(self):
        mock = MockObject("mock class", [
            ShouldBeCalled("__init__"),
            ShouldBeCalled("function").with_args((1,2))
        ])
        obj = mock()
        obj.function(1,2,3)
        
        self.assertRaises(MockVerificationFailure, mock._instance.verify)

if __name__ == "__main__":
    unittest.main()

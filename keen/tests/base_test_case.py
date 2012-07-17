import string
import unittest

__author__ = 'dkador'

class BaseTestCase(unittest.TestCase):
    # --------------------
    # Magic for snake_case
    # --------------------

    class __metaclass__(type):
        def __getattr__(cls, name):
            """

            This provides snake_case aliases for mixedCase @classmethods.

            For instance, if you were to ask for `cls.tear_down_class`, and it
            didn't exist, you would transparently get a reference to
            `cls.tearDownClass` instead.

            """

            name = BaseTestCase.to_mixed(name)
            return type.__getattribute__(cls, name)


    def __getattr__(self, name):
        """

        This provides snake_case aliases for mixedCase instance methods.

        For instance, if you were to ask for `self.assert_equal`, and it
        didn't exist, you would transparently get a reference to
        `self.assertEqual` instead.

        """

        mixed_name = BaseTestCase.to_mixed(name)
        mixed_attr = None

        try:
            mixed_attr = object.__getattribute__(self, mixed_name)
        except TypeError:
            pass

        if mixed_attr:
            return mixed_attr

        return self.__getattribute__(name)

    @classmethod
    def to_mixed(cls, underscore_input):
        """

        Transforms an input string from underscore_separated to mixedCase

        mixedCaseLooksLikeThis

        """

        word_list = underscore_input.split('_')
        word_count = len(word_list)
        if word_count > 1:
            for i in range(1, word_count):
                word_list[i] = string.capwords(word_list[i])
        ret = ''.join(word_list)
        return ret
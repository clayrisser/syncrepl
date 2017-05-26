#!/usr/bin/env python
# vim: ts=4 sw=4 et

# syncrepl_client callback code.
#
# Refer to the AUTHORS file for copyright statements.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Python 2 support
from __future__ import print_function

from sys import stdout


class BaseCallback(object):
    """
    :class:`BaseCallback` is a class containing all of the callbacks which
    :class:`syncrepl_client.Syncrepl` may call.  It is implemented as a new-style
    class, with class methods (although :class:`syncrepl_client.Syncrepl` doesn't
    care).

    This class exists for two reasons:

    * It documents each callback, the parameters the callback receives, and
      what the callback means.

    * It gives you a useful base class to sink unwanted callbacks.  If you only
      care about certain callbacks, you can implement them in your class, and let
      all the other callbacks percolate up to this class, where they are received
      and ignored.

    Another reason for using classes is because they can be stacked.  For
    example, if you want to handle callbacks, but you also want them to be
    logged, you can have your callback class use :class:`LoggingCallback` as a
    base class, and then set :attr:`LoggingCallback.dest` to the log sink.
    """

    @classmethod
    def bind_complete(cls, ldap):
        """Called to mark a successful bind to the LDAP server.

        :param ldap.LDAPObject ldap: The LDAP object.

        :return: None - any returned value is ignored.

        This callback is used to indicate a successful bind, and to give you
        one opportunity to interact with the LDAP server, before the connection
        is taken over by the syncrepl search.

        For example, if you want to record the bind DN (which you might not
        know, if you are doing things like a SASL bind), or you want to
        retrieve the schema stored on the server, this is the time to do it!

        This is the very first callback to be called.  Once the callback
        completes, the syncrepl search will begin, and other callbacks will
        start coming in.

        .. note::

            Once the callback has completed, there is no guarantee that `ldap`
            will still be a valid reference.

        .. warning::

            If you start any asynchronous operations (which includes searches),
            those operations **must** be completed before this callback
            returns.

        .. warning::

            Please do not unbind `ldap` from the LDAP server!

        .. warning::

            Once the callback completes, this LDAP connection will be used for
            the syncrepl search.  *No other operations will be allowed!**  If you
            want to communicate with the LDAP server after this callback
            completes, you will need to set up a separate LDAP connection.
        """
        pass

    @classmethod
    def refresh_done(cls):
        """Called to mark the end of the refresh phase.

        :return: None -- any returned value is ignored.

        .. note::

            This callback is **not** used when you are in refresh-only mode.
            This callback is only used in refresh-and-persist mode.

        When receiving this callback, you know that the refresh phase has 
        completed, and your view of the directory is now consistent with the 
        LDAP server (at least, the part of the directory which 
        matches your search and your access).

        If you need to do any sort of synchronization with anyone else, this is 
        the best time to do it.  Once you return from this callback, the 
        persist phase will begin.

        If you are operating in refresh-only mode, instead of receiving a 
        `refresh_done` callback, :meth:`syncrepl_client.poll` will return 
        :class:`False`.
        """
        pass

    @classmethod
    def record_add(cls, dn, attrs):
        """Called to indicate the addition of a new LDAP record.

        :param bytes dn: The DN of the added record.

        :param attrs: The record's attributes.
        :type attrs: Dict of lists of bytes

        :return: None - any returned value is ignored.

        .. warning::

            :data:`attrs` is passed by reference.  If you manipulate the
            dictionary—or its contents—in any way; you will pay for it later!

        This callback can happen in all modes, and in all phases, to indicate 
        that an entry has been added to your view of the search results.  In 
        refresh-only mode, and the refresh phase of refresh-and-perist mode, 
        the addition may have taken place at any time since your last update.  
        In the persist phase of refresh-and-persist mode, a new entry has just 
        been added—or modified—such that it matches your search.
        
        Attributes which are not present in the record are not present in the
        dictionary.  Dict keys are attribute names, and dict values are arrays
        (to support multi-valued attributes).

        .. note::

            Just because the dict values are arrays, does not mean that all
            attributes are multi-values.  The LDAP client does not know which
            attributes are single- and which are multi-valued, so it assumes
            that all are multi-valued.
            
            To learn which attributes are single- or multi-valued, you need to
            look at the schema, possibly using :mod:`ldap.schema`.
        """
        pass

    @classmethod
    def record_delete(cls, dn):
        """Called to indicate the deletion of an LDAP record.

        :param bytes dn: The DN of the deleted record.

        :return: None - any returned value is ignored.

        This callback can happen in all modes, and in all phases, to indicate 
        that an entry has been either been deleted, or that it no longer 
        matches your search.  In refresh-only mode, and the refresh phase of 
        refresh-and-perist mode, the deletion may have taken place at any time 
        since your last update.  In the persist phase of refresh-and-persist 
        mode, the entry has just disappeared.
        """
        pass

    @classmethod
    def record_rename(cls, old_dn, new_dn):
        """Called to indicate a change in DN.

        :param bytes old_dn: The old DN.

        :param bytes new_dn: The new DN.

        :return: None - any returned value is ignored.

        This callback happens when an entry's DN changes.

        This callback can happen in all modes, and in all phases, to indicate 
        that an entry's DN has been changed.  In refresh-only mode, and the 
        refresh phase of refresh-and-perist mode, the change may have taken 
        place at any time since your last update.  In the persist phase of 
        refresh-and-persist mode, the entry has just changed.

        You should expect a call to :meth:`record_change()` shortly after this 
        callback completes.
        """
        pass

    @classmethod
    def record_change(cls, dn, old_attrs, new_attrs):
        """Called to indicate a change in attributes.

        :param bytes dn: The DN of the changed record.

        :param dict old_attrs: The old attributes.

        :param dict new_attrs: The new attributes.

        :return: None - any returned value is ignored.

        This callback happens when an entry has changed.

        You are provided with the old attributes, and the new attributes.  It
        is up to you to determine what the changes are (if you care).

        .. note::

            If you look back at :meth:`record_add`, see the note about changing
            :data:`attrs`, and how it will come back to bite you?  Well, here's
            where it comes back to bite you!

        .. warning::

            :data:`new_attrs` is passed by reference.  If you manipulate the
            dictionary—or its contents—in any way; you will pay for it later!

        This callback can happen in all modes, and in all phases, to indicate 
        that an entry has been changed.  In refresh-only mode, and the 
        refresh phase of refresh-and-perist mode, the change may have taken 
        place at any time since your last update.  In the persist phase of 
        refresh-and-persist mode, the entry has just changed.

        .. note::

            Just because the dict values are arrays, does not mean that all
            attributes are multi-values.  The LDAP client does not know which
            attributes are single- and which are multi-valued, so it assumes
            that all are multi-valued.
            
            To learn which attributes are single- or multi-valued, you need to
            look at the schema, possibly using :mod:`ldap.schema`.
        """
        pass

    @classmethod
    def debug(cls, message):
        """Called to log debug messages.

        :param str message: A message of some sort.

        :return: None - any returned value is ignored.

        This method doesn't have much of a use.  It's just a way for
        :class:`syncrepl_client.Syncrepl` to log debug messages.  There's no
        guarantee that you'll get anything meaningful, or anything at all.
        """
        pass


class LoggingCallback(BaseCallback):
    """
    :class:`LoggingCallback` is a callback class which logs each callback.  It
    is useful for debugging purposes, as the output is not meant to be
    machine-readable.

    Each callback will cause messages to be printed to the file set in
    :attr:`dest`.  For the :meth:`bind_complete` callback, the bind DN is
    printed.  For callbacks containing DNs, the DNs are printed.  For callbacks
    containing attribute dictionaries, each dictionary's contents are printed.

    For a list of callbacks, and what they mean, see :class:`BaseCallback`.
    """

    dest = stdout
    """The log destination.

    This can be anything which can be used in :func:`print`'s `file` parameter.

    Defaults to :attr:`sys.stdout`.
    """

    @classmethod
    def bind_complete(cls, ldap):
        print('BIND COMPLETE!', file=cls.dest)
        print("\tWE ARE:", ldap.whoami_s(), file=cls.dest)

    @classmethod
    def refresh_done(cls):
        print('REFRESH COMPLETE!', file=cls.dest)

    @classmethod
    def record_add(cls, dn, attrs):
        print('NEW RECORD:', dn, file=cls.dest)
        for attr in attrs.keys():
            print("\t", attr, sep='', file=cls.dest)
            for value in attrs[attr]:
                print("\t\t", value, sep='', file=cls.dest)


    @classmethod
    def record_delete(cls, dn):
        print('DELETED RECORD:', dn, file=cls.dest)

    @classmethod
    def record_rename(cls, old_dn, new_dn):
        print('RENAMED RECORD:', file=cls.dest)
        print("\tOld:", old_dn, file=cls.dest)
        print("\tNew:", new_dn, file=cls.dest)

    @classmethod
    def record_change(cls, dn, old_attrs, new_attrs):
        print('RECORD CHANGED:', dn, file=cls.dest)
        for attr in new_attrs.keys():
            print("\t", attr, sep='', file=cls.dest)
            for value in new_attrs[attr]:
                print("\t\t", value, sep='', file=cls.dest)

    @classmethod
    def debug(cls, message):
        print('[DEBUG]', message, file=cls.dest)

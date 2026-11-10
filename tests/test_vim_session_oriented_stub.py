# VMware vSphere Python SDK tests
#
# Copyright (c) 2017-2024 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc. and/or its subsidiaries.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy
import tests

from pyVim import connect
from pyVmomi import SoapAdapter, vim


class SoapAdapterTests(tests.VCRTestBase):
    def test_invoke_method_login_session_exception(self):
        def login_fail(*args, **kwargs):
            raise vim_session.SESSION_EXCEPTIONS[0]()

        stub = connect.SoapStubAdapter()
        vim_session = connect.VimSessionOrientedStub(stub, login_fail)
        self.assertRaises(
            vim.fault.NotAuthenticated,
            vim_session.InvokeAccessor,
            "mo",
            "info"
        )

    def test_session_oriented_stub_deepcopy(self):
        stub = connect.SoapStubAdapter(
            host="example.com", version="vim.version.version1"
        )
        session_stub = SoapAdapter.SessionOrientedStub(stub, lambda s: None)
        copied_session_stub = copy.deepcopy(session_stub)
        self.assertIs(copied_session_stub, session_stub)

        login_method = connect.VimSessionOrientedStub.makeUserLoginMethod(
            "admin", "pass"
        )
        vim_session = connect.VimSessionOrientedStub(stub, login_method)
        copied_vim_session = copy.deepcopy(vim_session)
        self.assertIs(copied_vim_session, vim_session)

    def test_managed_object_deepcopy_with_session_oriented_stub(self):
        stub = connect.SoapStubAdapter(
            host="example.com", version="vim.version.version1"
        )
        login_method = connect.VimSessionOrientedStub.makeUserLoginMethod(
            "admin", "pass"
        )
        vim_session = connect.VimSessionOrientedStub(stub, login_method)
        si = vim.ServiceInstance("ServiceInstance", vim_session)

        si_copy = copy.deepcopy(si)
        self.assertEqual(str(si_copy), str(si))
        self.assertIs(si_copy._stub, vim_session)

        # Also verify collection deepcopy containing managed objects
        objects_list = [si, si]
        list_copy = copy.deepcopy(objects_list)
        self.assertEqual(len(list_copy), 2)
        self.assertIs(list_copy[0]._stub, vim_session)

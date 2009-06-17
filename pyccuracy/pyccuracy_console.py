#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 Bernardo Heynemann <heynemann@gmail.com>
# Copyright (C) 2009 Gabriel Falcão <gabriel@nacaolivre.org>
#
# Licensed under the Open Software License ("OSL") v. 3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.opensource.org/licenses/osl-3.0.php
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import codecs
import os
import sys, optparse
from pyccuracy.core import PyccuracyCore
from pyccuracy.common import Status
from pyccuracy.story_runner import StoryRunner, ParallelStoryRunner
from pyccuracy import Version, Release
from pyccuracy.colored_terminal import ProgressBar

__version_string__ = "pyccuracy %s (release '%s')" % (Version, Release)
__docformat__ = 'restructuredtext en'

# fixing print in non-utf8 terminals
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

no_progress = False
prg = None

def create_progress():
    global no_progress
    global prg
    if not no_progress:
        prg = ProgressBar("Pyccuracy - %s" % __version_string__)
        prg.update(0, 'Running first test...')

def update_progress(fixture, scenario, scenario_index):
    global no_progress
    global prg
    if not no_progress:
        if scenario.status == Status.Failed:
            prg.set_failed()
        total_scenarios = fixture.count_total_scenarios()
        if total_scenarios == 0:
            return

        current_progress = float(scenario_index) / total_scenarios
        prg.update(current_progress, "Scenario %d of %d - %s - %.2f secs" % (scenario_index, total_scenarios, scenario.title, fixture.ellapsed()))

def main():
    """ Main function - parses args and runs action """
    global no_progress

    extra_browser_driver_arguments = "\n\nThe following extra browser driver arguments " \
                                     " are supported in the key=value format:\n\nSelenium Browser Driver:\n" \
                                     "* selenium.server=ip or name of selenium server or grid\n" \
                                     "* selenium.port=port of the given selenium server or grid\n"

    parser = optparse.OptionParser(usage="%prog or type %prog -h (--help) for help" + extra_browser_driver_arguments, description=__doc__, version=__version_string__)
    parser.add_option("-p", "--pattern", dest="pattern", default="*.acc", help="File pattern. Defines which files will get executed [default: %default].")
    parser.add_option("-s", "--scenarios", dest="scenarios_to_run", default=None, help="Run only the given scenarios, comma separated. I.e: --scenarios=1,4,9")
    parser.add_option("-l", "--language", dest="language", default="en-us", help="Language. Defines which language the dictionary will be loaded with  [default: %default].")
    parser.add_option("-L", "--languagesdir", dest="languages_dir", default=None, help="Languages Directory. Defines where Pyccuracy will search for language dictionaries  [default: %default].")
    parser.add_option("-d", "--dir", dest="dir", default=os.curdir, help="Tests directory. Defines where the tests to be executed are [default: %default]. Note: this is recursive, so all the tests under the current directory get executed.")
    parser.add_option("-a", "--actionsdir", dest="actions_dir", default=None, help="Actions directory. Defines where the Pyccuracy actions are. Chances are you don't need to change this parameter [default: %default].")
    parser.add_option("-A", "--customactionsdir", dest="custom_actions_dir", default=None, help="Custom Actions directory. Defines where the Pyccuracy custom actions are. If you don't change this parameter Pyccuracy will use the tests directory [default: %default].")
    parser.add_option("-P", "--pagesdir", dest="pages_dir", default=None, help="Pages directory. Defines where the Pyccuracy custom pages are. If you don't change this parameter Pyccuracy will use the tests directory [default: %default].")
    parser.add_option("-u", "--url", dest="url", default=None, help="Base URL. Defines a base url against which the tests will get executed. For more details check the documentation [default: %default].")
    parser.add_option("-b", "--browser", dest="browser_to_run", default="firefox", help="Browser to run. Browser driver will use it to run tests [default: %default].")
    parser.add_option("-w", "--workers", dest="workers", default=1, help="Workers to run in parallel [default: %default].")

    #browser driver
    parser.add_option("-e", "--browserdriver", dest="browser_driver", default="selenium", help="Browser Driver to be used on tests. [default: %default].")

    #throws
    parser.add_option("-T", "--throws", dest="should_throw", default=False, help="Should Throw. Defines whether Pyccuracy console should throw an exception when tests fail. This is useful to set to True if you are running Pyccuracy inside unit tests [default: %default].")

    #reporter
    parser.add_option("-R", "--report", dest="write_report", default="true", help="Should write report. Defines if Pyccuracy should write an html report after each run [default: %default].")
    parser.add_option("-D", "--reportdir", dest="report_dir", default=os.curdir, help="Report directory. Defines the directory to write the report in [default: %default].")
    parser.add_option("-F", "--reportfile", dest="report_file_name", default="report.html", help="Report file. Defines the file name to write the report with [default: %default].")

    options, args = parser.parse_args()

    workers = options.workers and int(options.workers) or None
    pyc = PyccuracyCore()

    extra_args = {}
    if args:
        for arg in args:
            if arg == "noprogress":
                no_progress = True
                continue
            if not "=" in arg:
                raise ValueError("The specified extra argument should be in the form of key=value and not %s" % arg)
            key, value = arg.split('=')
            extra_args[key] = value

    create_progress()

    result = pyc.run_tests(actions_dir=options.actions_dir,
                           custom_actions_dir=options.custom_actions_dir,
                           pages_dir=options.pages_dir,
                           languages_dir=options.languages_dir,
                           file_pattern=options.pattern,
                           scenarios_to_run=options.scenarios_to_run,
                           tests_dir=options.dir,
                           base_url=options.url,
                           default_culture=options.language,
                           write_report=options.write_report.lower() == "true",
                           report_file_dir=options.report_dir,
                           report_file_name=options.report_file_name,
                           browser_to_run=options.browser_to_run,
                           browser_driver=options.browser_driver,
                           should_throw=options.should_throw,
                           workers=workers,
                           extra_args=extra_args,
                           on_scenario_started=update_progress,
                           on_scenario_completed=update_progress)

    if not result or result.get_status() != "SUCCESSFUL":
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()

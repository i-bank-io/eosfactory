#pragma once

#include <teoslib/config.h>
#include <teos/command/command.hpp>

namespace teos
{
  namespace command
  {
    class VersionClient : public TeosCommand
    {
    public:

      VersionClient(ptree reqJson, bool raw = false) : TeosCommand(
        "", reqJson, raw) {
        stringstream ss;
        ss << PROJECT_NAME << " " <<VERSION_MAJOR << "." << VERSION_MINOR;
        respJson_.put("version", ss.str());
      }
    };

    class VersionClientOptions : public CommandOptions
    {
    public:
      VersionClientOptions(int argc, const char **argv)
        : CommandOptions(argc, argv) {}

    protected:
      const char* getUsage() {
        return R"EOF(
Retrieve version information of the client
Usage: ./teos version client [Options]
Usage: ./teos version client [-j '{}'] [OPTIONS]
)EOF";
      }

      bool setJson(variables_map &vm) {
        return true;
      }

      TeosCommand getCommand(bool is_raw) {
        return VersionClient(reqJson, is_raw);
      }

      void getOutput(TeosCommand command) {
        output("Version", "%s", GET_STRING(command, "version"));
      }

      void getExample() {
        cout << R"EOF(
boost::property_tree::ptree reqJson;
VersionClient versionClient(reqJson);
cout << versionClient.responseToString() << endl;
/*
printout:
)EOF" << endl;

        boost::property_tree::ptree reqJson;
        VersionClient versionClient(reqJson);
        cout << versionClient.responseToString() << endl;

      cout << R"EOF(
*/
)EOF" << endl;
      }
    };

  }
}
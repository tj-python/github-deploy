import os

import asyncclick as click

plugin_folder = os.path.join(os.path.dirname(__file__), "commands")


class GithubDeploy(click.MultiCommand):
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(plugin_folder):
            if (
                    filename.endswith(".py")
                    and not filename.startswith("__init__")
                    and not filename.startswith("_")
            ):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        ns = {}
        fn = os.path.join(plugin_folder, name + ".py")

        if os.path.exists(fn):
            with open(fn) as f:
                code = compile(f.read(), fn, "exec")
                eval(code, ns, ns)
            return ns["main"]

        ctx.fail(f"Invalid Command \"{name}\"")


main = GithubDeploy(
    help=(
        "Deploy changes to multiple github repositories using "
        "a single command."
    ),
)

if __name__ == "__main__":
    main()

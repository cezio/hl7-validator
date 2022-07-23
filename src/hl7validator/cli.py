import io

import click

from .validator import Validator


@click.command("validate_hl7")
@click.argument("rules", type=click.File("rt"))
@click.argument("message", type=click.File("rb"))
@click.option("-q", "--quiet", is_flag=True, default=False)
@click.pass_context
def main(
    click_ctx: click.Context, rules: io.TextIOBase, message: io.BytesIO, quiet=False
):
    v = Validator(rules=rules.read())
    ctx = v.validate(message.read())
    if not ctx.is_valid:
        if not quiet:
            click.echo("Message is invalid:")
            for log_msg in ctx.log:
                if log_msg.is_error:
                    click.echo(f" * {log_msg.msg} | {str(log_msg.rule)}")
        click_ctx.exit(1)
    if not quiet:
        click.echo("Message is valid.")
    click_ctx.exit(0)


if __name__ == "__main__":
    main()

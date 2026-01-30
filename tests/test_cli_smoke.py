from pcb_render import cli


def test_help_parses():
	args = cli.parse_args(["render", "board.json", "--format", "svg", "--dpi", "300"])
	assert args.command == "render"
	assert args.format == "svg"

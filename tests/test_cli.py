from typer.testing import CliRunner

from discovery_zero.cli import app

runner = CliRunner()


class TestCLI:
    def test_init(self, tmp_graph_dir):
        path = tmp_graph_dir / "graph.json"
        result = runner.invoke(app, ["init", "--path", str(path)])
        assert result.exit_code == 0
        assert path.exists()

    def test_summary_empty(self, tmp_graph_dir):
        path = tmp_graph_dir / "graph.json"
        runner.invoke(app, ["init", "--path", str(path)])
        result = runner.invoke(app, ["summary", "--path", str(path)])
        assert result.exit_code == 0
        assert "0 nodes" in result.stdout

    def test_add_node(self, tmp_graph_dir):
        path = tmp_graph_dir / "graph.json"
        runner.invoke(app, ["init", "--path", str(path)])
        result = runner.invoke(
            app, ["add-node", "--path", str(path),
                  "--statement", "Two points determine a line",
                  "--belief", "1.0"]
        )
        assert result.exit_code == 0
        assert "Added node" in result.stdout

    def test_show_nodes(self, tmp_graph_dir):
        path = tmp_graph_dir / "graph.json"
        runner.invoke(app, ["init", "--path", str(path)])
        runner.invoke(
            app, ["add-node", "--path", str(path),
                  "--statement", "Axiom 1", "--belief", "1.0"]
        )
        result = runner.invoke(app, ["show", "--path", str(path)])
        assert result.exit_code == 0
        assert "Axiom 1" in result.stdout

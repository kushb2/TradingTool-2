import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Button,
  Card,
  Col,
  Divider,
  Layout,
  List,
  Row,
  Space,
  Tag,
  Typography,
} from "antd";

const BACKEND_URL = "https://tradingtool-2.onrender.com";
const FRONTEND_URL = "https://kushb2.github.io/TradingTool-2/";
const REPO_URL = "https://github.com/kushb2/TradingTool-2";

function App() {
  const [backendStatus, setBackendStatus] = useState("Checking...");
  const [backendTagColor, setBackendTagColor] = useState("processing");

  const quickActions = useMemo(
    () => [
      {
        title: "Open Frontend",
        href: FRONTEND_URL,
        type: "primary",
      },
      {
        title: "Open Backend",
        href: BACKEND_URL,
        type: "default",
      },
      {
        title: "Open Repository",
        href: REPO_URL,
        type: "default",
      },
    ],
    []
  );

  const runbook = useMemo(
    () => [
      "poetry run python -m src.presentation.cli.telegram_webhook_cli info",
      "poetry run python -m src.presentation.cli.telegram_cli send --text \"Ping from TradingTool-2\"",
      "poetry run uvicorn src.presentation.api.telegram_webhook_app:app --host 0.0.0.0 --port 8000 --reload",
    ],
    []
  );

  useEffect(() => {
    let isMounted = true;

    async function checkBackend() {
      try {
        const response = await fetch(BACKEND_URL, { cache: "no-store" });
        if (!isMounted) {
          return;
        }
        if (response.ok) {
          setBackendStatus("Reachable");
          setBackendTagColor("success");
        } else {
          setBackendStatus(`HTTP ${response.status}`);
          setBackendTagColor("warning");
        }
      } catch (_error) {
        if (!isMounted) {
          return;
        }
        setBackendStatus("Unreachable");
        setBackendTagColor("error");
      }
    }

    checkBackend();
    const intervalId = window.setInterval(checkBackend, 45000);

    return () => {
      isMounted = false;
      window.clearInterval(intervalId);
    };
  }, []);

  return (
    <Layout>
      <Layout.Content>
        <Card title="TradingTool-2" extra={<Tag color="blue">Ant Design UI</Tag>}>
          <Space direction="vertical" size="large">
            <Typography.Paragraph>
              GitHub Pages React interface for monitoring deployment status,
              Telegram integration flow, and operator runbook commands.
            </Typography.Paragraph>

            <Row gutter={[16, 16]}>
              <Col xs={24} md={8}>
                <Card title="Frontend" size="small">
                  <Space direction="vertical">
                    <Typography.Text>{FRONTEND_URL}</Typography.Text>
                    <Tag color="success">Live</Tag>
                  </Space>
                </Card>
              </Col>

              <Col xs={24} md={8}>
                <Card title="Backend" size="small">
                  <Space direction="vertical">
                    <Typography.Text>{BACKEND_URL}</Typography.Text>
                    <Tag color={backendTagColor}>{backendStatus}</Tag>
                  </Space>
                </Card>
              </Col>

              <Col xs={24} md={8}>
                <Card title="Telegram Mode" size="small">
                  <Space direction="vertical">
                    <Typography.Text>Webhook + FastAPI</Typography.Text>
                    <Tag color="success">Configured</Tag>
                  </Space>
                </Card>
              </Col>
            </Row>

            <Divider />

            <Space wrap>
              {quickActions.map((action) => (
                <Button
                  key={action.title}
                  type={action.type}
                  href={action.href}
                  target="_blank"
                >
                  {action.title}
                </Button>
              ))}
            </Space>

            <Card title="Operator Runbook" size="small">
              <List
                size="small"
                dataSource={runbook}
                renderItem={(command) => (
                  <List.Item>
                    <Typography.Text code copyable>
                      {command}
                    </Typography.Text>
                  </List.Item>
                )}
              />
            </Card>

            <Alert
              type="info"
              message="Deployment Note"
              description="For GitHub Pages deployment, run npm run deploy after committing UI changes."
              showIcon
            />
          </Space>
        </Card>
      </Layout.Content>
    </Layout>
  );
}

export default App;

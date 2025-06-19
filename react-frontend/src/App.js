import React from "react";
import { Routes, Route } from "react-router-dom";
import { Layout, Menu, Typography } from "antd";
import {
  BookOutlined,
  SearchOutlined,
  StarOutlined,
  FilterOutlined,
} from "@ant-design/icons";
import HomePage from "./components/HomePage";
import SearchPage from "./components/SearchPage";
import BookDetailsPage from "./components/BookDetailsPage";
import RecommendationsPage from "./components/RecommendationsPage";
import { Link, useLocation } from "react-router-dom";

const { Header, Content } = Layout;
const { Title } = Typography;

function App() {
  const location = useLocation();

  const menuItems = [
    {
      key: "/",
      icon: <BookOutlined />,
      label: <Link to="/">Home</Link>,
    },
    {
      key: "/search",
      icon: <SearchOutlined />,
      label: <Link to="/search">Search Books</Link>,
    },
    {
      key: "/recommendations",
      icon: <StarOutlined />,
      label: <Link to="/recommendations">Recommendations</Link>,
    },
  ];

  return (
    <Layout>
      <Header style={{ background: "#001529", padding: "0 24px" }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center" }}>
            <BookOutlined
              style={{
                fontSize: "24px",
                color: "#1890ff",
                marginRight: "12px",
              }}
            />
            <Title level={3} style={{ color: "white", margin: 0 }}>
              Goodreads Recommender
            </Title>
          </div>
          <Menu
            theme="dark"
            mode="horizontal"
            selectedKeys={[location.pathname]}
            items={menuItems}
            style={{ backgroundColor: "transparent", borderBottom: "none" }}
          />
        </div>
      </Header>

      <Content style={{ padding: "24px", minHeight: "calc(100vh - 64px)" }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/book/:id" element={<BookDetailsPage />} />
          <Route path="/recommendations" element={<RecommendationsPage />} />
        </Routes>
      </Content>
    </Layout>
  );
}

export default App;

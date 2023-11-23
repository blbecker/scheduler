import {Card, Col, Divider, Layout, MenuProps, Row, theme} from 'antd';

import React from 'react';
import Sidebar from "@/app/components/sidebar";
import NavHeader from "@/app/components/nav-header";

const {Header, Content, Sider} = Layout;

const items1: MenuProps['items'] = ['1', '2', '3'].map((key) => ({
    key,
    label: `nav ${key}`,
}));

const Home = function Home() {
    // const {
    //     token: {colorBgContainer},
    // } = theme.useToken();

    return (
        <Layout>
            <NavHeader/>
            <Layout>
                <Sidebar/>
                <Layout style={{padding: '0 24px 24px'}}>
                    <Divider orientation="left">Home Panel</Divider>
                    <Row gutter={16}>
                        <Col className="gutter-row" span={6}>
                            <Card title='Some Data'>Some data goes here</Card>
                        </Col>
                        <Col className="gutter-row" span={6}>
                            <Card title='More Data'>Some more data goes here</Card>
                        </Col>
                        <Col className="gutter-row" span={12}>
                            <Card title='Last of the data'>Lying data goes here</Card>
                        </Col>
                    </Row>
                </Layout>
            </Layout>
        </Layout>
    );
}

export default Home;
'use client';

import {Card, Col, Divider, Layout, MenuProps, Row, theme} from 'antd';

import React from 'react';
import Sidebar from "@/app/components/sidebar";
import NavHeader from "@/app/components/header";
import UserTable from "@/app/components/users/user-table";

const {Content, Sider} = Layout;

const items1: MenuProps['items'] = ['1', '2', '3'].map((key) => ({
    key,
    label: `nav ${key}`,
}));

const style: React.CSSProperties = {background: '#0092ff', padding: '8px 0'};

const Admin = function Admin() {
    const {
        token: {colorBgContainer},
    } = theme.useToken();

    return (
        <Layout>
            <NavHeader/>
            <Layout>
                <Sidebar/>
                <Layout style={{padding: '0 24px 24px'}}>
                    <Divider orientation="left">Admin Panel</Divider>
                    <Row gutter={[{ xs: 8, sm: 16, md: 24, lg: 32 },{ xs: 8, sm: 16, md: 24, lg: 32 }]}>
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
                    <Divider orientation='left'>Users</Divider>
                    <Row gutter={[{ xs: 8, sm: 16, md: 24, lg: 32 },{ xs: 8, sm: 16, md: 24, lg: 32 }]}>
                        <Col className="gutter-row" span={24}>
                            <UserTable/>
                        </Col>
                    </Row>
                </Layout>
            </Layout>
        </Layout>
    );
}

export default Admin;
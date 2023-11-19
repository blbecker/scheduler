'use client';

import {Layout, Menu, MenuProps, theme} from 'antd';
import React, {FC, useState} from 'react';
import Link from "next/link";

// const {Header, Content, Sider} = Layout;
const { Header, Content, Sider } = Layout;

const items1: MenuProps['items'] = ['1', '2', '3'].map((key) => ({
    key,
    label: `Nav ${key}`,
}));
const NavHeader: FC = () => {
    // const {
    //     token: {colorBgContainer},
    // } = theme.useToken();

    return (
        <Header style={{display: 'flex', alignItems: 'center'}}>
            <div className="demo-logo"/>
            <Menu style={{flex: '1'}} theme="dark" mode="horizontal" defaultSelectedKeys={['2']} items={[
                {
                    key: '/',
                    label: <Link href='/'>Home</Link>
                },
                {
                    key: '/admin',
                    label: <Link href='/admin/'>Admin</Link>
                }
            ]}/>
        </Header>
    );
};

export default NavHeader
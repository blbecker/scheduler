'use server';

import {Layout, Menu, MenuProps, Space, Table, Tag, theme} from 'antd';
import React, {FC} from 'react';
import {ColumnsType} from "antd/lib/table";
import {iWorker} from "@/app/models/worker";

async function getWorkers() {
    const res = await fetch('http://api:3000/workers', { cache: 'no-store' })
    // The return value is *not* serialized
    // You can return Date, Map, Set, etc.

    if (!res.ok) {
        // This will activate the closest `error.js` Error Boundary
        throw new Error('Failed to fetch data')
    }

    return res.json()
}

const columns: ColumnsType<iWorker> = [
    {
        title: 'Family Name',
        dataIndex: 'family_name',
        key: 'familyName',
    },
    {
        title: 'Given Name',
        dataIndex: 'given_name',
        key: 'familyName',
    },

];

const UserTable: FC = async () => {
    // const {
    //     token: {colorBgContainer},
    // } = theme.useToken();

    // const data = await getWorkers()
    let data = '[{"given_name":"Tony","family_name":"Stark"},{"given_name":"Bruce","family_name":"Banner"}]'
    const worker: iWorker[] = JSON.parse(data)

    // let datastring = data.len

    return (
        <>
            <Table columns={columns} dataSource={worker}/>
        </>
    );
};

export default UserTable
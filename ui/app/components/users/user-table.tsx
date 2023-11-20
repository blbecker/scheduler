'use server';

import {Table} from 'antd';
import React, {FC} from 'react';
import {ColumnsType} from "antd/lib/table";
import {iWorker} from "@/app/models/worker";

async function getWorkers() {
    const res = await fetch('http://api:3000/workers', {cache: 'no-store'})
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
        title: 'ID',
        dataIndex: 'id',
        key: 'id',
    },
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

    const data = await getWorkers()

    return (
        <>
            <Table columns={columns} dataSource={data}/>
        </>
    );
};

export default UserTable
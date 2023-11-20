'use server';

import {Table} from 'antd';
import React, {FC} from 'react';
import {ColumnsType} from "antd/lib/table";
import {iWorkerColumnsType} from "@/app/models/worker";

async function getWorkers() {
    const api_server_url = process.env.API_SERVER_URL
    const res = await fetch(api_server_url+'/workers', {cache: 'no-store'})

    if (!res.ok) {
        // This will activate the closest `error.js` Error Boundary
        throw new Error('Failed to fetch data')
    }

    return res.json()
}

const WorkerTable: FC = async () => {
    const data = await getWorkers()

    return (
        <>
            <Table columns={iWorkerColumnsType} dataSource={data}/>
        </>
    );
};

export default WorkerTable
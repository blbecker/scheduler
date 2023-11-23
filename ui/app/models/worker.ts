import {ColumnsType} from "antd/lib/table";

export interface iWorker {
    id: string
    family_name: string;
    given_name: string;
}

export const iWorkerColumnsType: ColumnsType<iWorker> = [
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
import StyledComponentsRegistry from '@/lib/AntdRegistry'
import {ConfigProvider, Layout} from 'antd'
import {Content} from 'antd/es/layout/layout'
import type {Metadata} from 'next'
import '@/app/globals.css'

export const metadata: Metadata = {
    title: 'Scheduler',
    description: 'For Schedulers',
}

export default function RootLayout({
                                       children,
                                   }: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
        <body>
        <Layout>
            <ConfigProvider
                theme={{
                    // algorithm: theme.darkAlgorithm,
                    token: {
                        // https://ant.design/docs/react/customize-theme
                    },
                }}
            >
                <Content>
                    <StyledComponentsRegistry>
                        {children}
                    </StyledComponentsRegistry>
                </Content>
            </ConfigProvider>
        </Layout>
        </body>

        </html>
    )
}

import type { Meta, StoryObj } from '@storybook/react-vite'
import { Alert, AlertDescription, AlertTitle } from './alert'
import { Badge } from './badge'
import { Button } from './button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from './dropdown-menu'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './select'
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from './sheet'
import { Skeleton } from './skeleton'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './table'
import { ThemeProvider } from '../../theme/ThemeProvider'

const meta = {
  title: 'Primitives/Controls',
  tags: ['autodocs', 'test'],
  decorators: [(Story) => <ThemeProvider defaultTheme="light"><Story /></ThemeProvider>],
} satisfies Meta

export default meta
type Story = StoryObj<typeof meta>

export const ButtonVariants: Story = { render: () => <div className="flex flex-wrap gap-3"><Button>Primary action</Button><Button variant="outline">Secondary action</Button><Button variant="ghost">Quiet action</Button></div> }
export const StatusBadges: Story = { render: () => <div className="flex gap-3"><Badge>Ready</Badge><Badge variant="secondary">Evaluation</Badge><Badge variant="outline">Exploratory</Badge></div> }
export const InformationalAlert: Story = { render: () => <Alert><AlertTitle>Evidence boundary</AlertTitle><AlertDescription>Prediction interval coverage is evaluated for one-step forecasts.</AlertDescription></Alert> }
export const SelectControl: Story = { render: () => <Select defaultValue="24"><SelectTrigger aria-label="Forecast horizon"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="12">12 months</SelectItem><SelectItem value="24">24 months</SelectItem></SelectContent></Select> }
export const LoadingSkeleton: Story = { render: () => <Skeleton className="h-24 w-full max-w-md" /> }
export const MobileSheet: Story = { render: () => <Sheet><SheetTrigger render={<Button variant="outline">Open navigation</Button>} /><SheetContent><SheetTitle>Primary navigation</SheetTitle><p className="text-sm text-muted-foreground">Five evidence destinations</p></SheetContent></Sheet> }
export const Dropdown: Story = { render: () => <DropdownMenu><DropdownMenuTrigger render={<Button variant="outline">Actions</Button>} /><DropdownMenuContent><DropdownMenuItem>View evidence</DropdownMenuItem><DropdownMenuItem>Copy provenance</DropdownMenuItem></DropdownMenuContent></DropdownMenu> }
export const DataTable: Story = { render: () => <Table><TableHeader><TableRow><TableHead>Metric</TableHead><TableHead>Value</TableHead></TableRow></TableHeader><TableBody><TableRow><TableCell>MAE</TableCell><TableCell>0.243 ppm</TableCell></TableRow></TableBody></Table> }

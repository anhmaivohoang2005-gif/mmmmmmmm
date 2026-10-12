<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LogiSpace Simulator - Sales Forwarding Edition</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- React & ReactDOM & Babel CDN -->
    <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
</head>
<body class="bg-slate-950 text-slate-100 font-sans">
    <div id="root"></div>

    <script type="text/babel">
        const { useState } = React;

        const PORTS_DATABASE = [
            { code: "VNVUT", name: "Cái Mép TCIT (VNVUT)", country: "Vietnam" },
            { code: "VNCLI", name: "Cát Lái (VNCLI)", country: "Vietnam" },
            { code: "VNHPH", name: "Hải Phòng (VNHPH)", country: "Vietnam" },
            { code: "VNDAD", name: "Đà Nẵng (VNDAD)", country: "Vietnam" },
            { code: "VNUIH", name: "Quy Nhơn (VNUIH)", country: "Vietnam" },
            { code: "CNSHA", name: "Shanghai (CNSHA)", country: "China" },
            { code: "CNNGB", name: "Ningbo (CNNGB)", country: "China" },
            { code: "CNYAN", name: "Shenzhen / Yantian (CNYAN)", country: "China" },
            { code: "CNTAO", name: "Qingdao (CNTAO)", country: "China" },
            { code: "KRPUS", name: "Busan (KRPUS)", country: "South Korea" },
            { code: "SGSIN", name: "Singapore (SGSIN)", country: "Singapore" },
            { code: "USLAX", name: "Los Angeles, CA (USLAX)", country: "United States" },
            { code: "USLGB", name: "Long Beach, CA (USLGB)", country: "United States" },
            { code: "USNYC", name: "New York / New Jersey (USNYC)", country: "United States" },
            { code: "NLRTM", name: "Rotterdam (NLRTM)", country: "Netherlands" },
            { code: "DEHAM", name: "Hamburg (DEHAM)", country: "Germany" },
            { code: "BEANR", name: "Antwerp (BEANR)", country: "Belgium" }
        ];

        const CONTAINER_TYPES = [
            "20'GP", "40'GP", "40'HC", "45'HC", "Reefer 20'", "Reefer 40'", "Open Top", "Flat Rack"
        ];

        const CARRIERS_LIST = [
            "Maersk Line", "CMA CGM", "MSC", "Evergreen", "Wan Hai Lines", "ONE (Ocean Network Express)", "Hapag-Lloyd"
        ];

        const INITIAL_QUOTATIONS = [
            {
                id: "QT-01", carrier: "Maersk Line", pol: "VNVUT", pod: "USLAX", containerType: "40'HC",
                etd: "2026-10-15", eta: "2026-10-30", oceanFreight: 3200, pss: 300, gri: 0, bafLss: 250,
                localCharges: 180, docFee: 50, trucking: 350, slotFee: 0, otherFees: 0,
                source: "LIVE", sourceName: "Maersk API Connect"
            },
            {
                id: "QT-02", carrier: "Wan Hai Lines", pol: "VNVUT", pod: "USLAX", containerType: "40'HC",
                etd: "2026-10-15", eta: "2026-10-30", oceanFreight: 3100, pss: 250, gri: 100, bafLss: 220,
                localCharges: 170, docFee: 50, trucking: 350, slotFee: 0, otherFees: 0,
                source: "MANUAL", sourceName: "Local Rate Sheet Q4"
            }
        ];

        const INITIAL_SPACES = [
            {
                id: "SP-01", pol: "VNVUT", pod: "USLAX", containerType: "40'HC", carrier: "Maersk Line",
                availableSpace: 3, source: "LIVE", sourceName: "Carrier Allocation Portal"
            }
        ];

        const INITIAL_SLOTS = [
            {
                id: "SLOT-01", provider: "Global Forwarder Vina", pol: "VNVUT", pod: "USLAX", carrier: "Evergreen",
                vesselVoyage: "EVER GIVEN 042E", containerType: "40'HC", remainingSlots: 3, sellingPrice: 4100,
                source: "DEMO", sourceName: "Slot Exchange Network"
            }
        ];

        const PEAK_EVENTS = [
            {
                id: "EVT-01", name: "Tet Nguyen Dan (Lunar New Year)",
                reason: "Nha may dong cua truoc Tet, nhu cau day hang truoc ky nghi tang vot, nguy co thieu vo container.",
                certainty: "Cao", source: "Historical shipping trend"
            },
            {
                id: "EVT-02", name: "Peak Season Q4 / Black Friday",
                reason: "Mua cao diem mua sam cuoi nam le hoi, nhu cau xuat khau sang Au My tang manh.",
                certainty: "Cao", source: "Global Market Forecast"
            }
        ];

        function calculateTotalCost(quotation, quantity) {
            if (!quotation) return 0;
            const unitItems = (quotation.oceanFreight || 0) + (quotation.pss || 0) + (quotation.gri || 0) + 
                              (quotation.bafLss || 0) + (quotation.localCharges || 0) + (quotation.docFee || 0) + 
                              (quotation.trucking || 0) + (quotation.slotFee || 0) + (quotation.otherFees || 0);
            return unitItems * quantity;
        }

        function calculateProfitMetrics(totalCost, sellingPricePerUnit, quantity, targetMarginPercent = 10) {
            if (!sellingPricePerUnit || sellingPricePerUnit <= 0 || quantity <= 0 || totalCost <= 0) {
                return { revenue: 0, grossProfit: 0, marginPercent: 0, minSellingPricePerUnit: totalCost > 0 ? (totalCost / quantity) / (1 - targetMarginPercent / 100) : 0, status: "Chua du du lieu" };
            }
            const revenue = sellingPricePerUnit * quantity;
            const grossProfit = revenue - totalCost;
            const marginPercent = (grossProfit / revenue) * 100;
            const minSellingPricePerUnit = (totalCost / quantity) / (1 - targetMarginPercent / 100);

            let status = "Chua dat muc tieu";
            if (Math.abs(grossProfit) <= 0.005) status = "Hoa von";
            else if (grossProfit < 0) status = "Thua lo";
            else if (marginPercent >= targetMarginPercent) status = "Dat muc tieu";

            return { revenue, grossProfit, marginPercent, minSellingPricePerUnit, status };
        }

        function calculateSpaceDeficit(demandQuantity, availableSpace) {
            const deficit = Math.max(0, demandQuantity - availableSpace);
            const fulfillmentRate = demandQuantity > 0 ? Math.min(100, (availableSpace / demandQuantity) * 100) : 100;
            return { deficit, fulfillmentRate };
        }

        function App() {
            const [shipmentState, setShipmentState] = useState({
                shipper: "QA Furniture Co., Ltd (Bình Phước)",
                consignee: "MTA Cabinets LLC (Texas)",
                sales: "Nguyễn Văn A (Sales Forwarding)",
                pol: "VNVUT",
                pod: "USLAX",
                containerType: "40'HC",
                quantity: 5,
                carrier: "Wan Hai Lines",
                commodity: "Wooden kitchen cabinets (HS 940340)",
                bookingDate: "2026-10-13",
                etd: "2026-10-15",
                eta: "2026-10-30",
                updatedAt: "12/10/2026 15:30"
            });

            const [draftShipment, setDraftShipment] = useState({ ...shipmentState });
            const [formErrors, setFormErrors] = useState({});
            const [etaWarning, setEtaWarning] = useState(false);
            const [targetMargin, setTargetMargin] = useState(10);
            const [activeTab, setActiveTab] = useState("dashboard");
            const [sellingPrices, setSellingPrices] = useState({ "QT-01": 5900, "QT-02": 5850 });
            const [slots, setSlots] = useState(INITIAL_SLOTS);
            const [successNotice, setSuccessNotice] = useState("");

            const handleDraftChange = (field, value) => {
                setDraftShipment(prev => ({ ...prev, [field]: value }));
            };

            const handleApplyAndUpdate = () => {
                let errors = {};
                if (!draftShipment.pol) errors.pol = "Chon POL.";
                if (!draftShipment.pod) errors.pod = "Chon POD.";
                if (draftShipment.pol === draftShipment.pod) errors.pod = "POL va POD khong duoc trung.";
                if (!draftShipment.quantity || draftShipment.quantity <= 0) errors.quantity = "So luong > 0.";

                if (draftShipment.eta && draftShipment.etd && draftShipment.eta < draftShipment.etd) {
                    setEtaWarning(true);
                    return;
                }

                if (Object.keys(errors).length > 0) {
                    setFormErrors(errors);
                    setSuccessNotice("");
                    return;
                }

                const nowStr = new Date().toLocaleString("vi-VN");
                const updated = { ...draftShipment, updatedAt: nowStr };
                setShipmentState(updated);
                setFormErrors({});
                setEtaWarning(false);
                setSuccessNotice(`Cập nhật lô hàng thành công lúc ${nowStr}! Tất cả phân hệ đã đồng bộ.`);
                setTimeout(() => setSuccessNotice(""), 5000);
            };

            const matchingQuotations = INITIAL_QUOTATIONS.filter(q => q.pol === shipmentState.pol && q.pod === shipmentState.pod && q.containerType === shipmentState.containerType);
            const matchingSpaces = INITIAL_SPACES.filter(s => s.pol === shipmentState.pol && s.pod === shipmentState.pod && s.containerType === shipmentState.containerType);
            const matchingSlots = slots.filter(sl => sl.pol === shipmentState.pol && sl.pod === shipmentState.pod && sl.containerType === shipmentState.containerType);

            return (
                <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
                    <header className="bg-slate-900 border-b border-slate-800 px-6 py-4 flex justify-between items-center shadow">
                        <div>
                            <h1 className="text-lg font-bold">LOGISPACE SIMULATOR <span className="text-xs bg-blue-600 px-2 py-0.5 rounded ml-2">Sales Forwarding Edition</span></h1>
                            <p className="text-xs text-slate-400">Hệ thống hỗ trợ Sales Forwarding, Báo giá cước, Dự báo Space & Sàn Slot</p>
                        </div>
                        <div className="text-right text-xs text-slate-300">
                            <p>Trạng thái: <span className="text-emerald-400 font-semibold">[Đã đồng bộ - Confirmed]</span></p>
                            <p>Cập nhật lần cuối: {shipmentState.updatedAt}</p>
                        </div>
                    </header>

                    {successNotice && (
                        <div className="bg-emerald-600 text-white px-6 py-2.5 text-xs text-center font-medium shadow">
                            {successNotice}
                        </div>
                    )}

                    <div className="flex-1 flex flex-col lg:flex-row">
                        <div className="w-full lg:w-96 bg-slate-900 border-r border-slate-800 p-4 flex flex-col shadow-sm overflow-y-auto">
                            <div className="flex justify-between items-center mb-3 pb-2 border-b border-slate-800">
                                <h2 className="font-bold text-slate-200 text-sm">THÔNG TIN LÔ HÀNG</h2>
                                <span className="text-[10px] bg-amber-500/20 text-amber-300 border border-amber-500/30 font-bold px-2 py-0.5 rounded">Đang chỉnh sửa (Nháp)</span>
                            </div>

                            <div className="space-y-4 flex-1 text-xs">
                                <div className="space-y-2 p-2.5 bg-slate-950/60 rounded border border-slate-800">
                                    <p className="font-bold text-blue-400 text-[11px] uppercase tracking-wider">1. Các Bên Liên Quan</p>
                                    <div>
                                        <label className="block text-slate-400 mb-1">Shipper (vd: QA Furniture Co., Ltd)</label>
                                        <input type="text" className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-slate-200" value={draftShipment.shipper} onChange={e => handleDraftChange('shipper', e.target.value)} placeholder="Nhập tên Shipper..." />
                                    </div>
                                    <div>
                                        <label className="block text-slate-400 mb-1">Consignee (vd: MTA Cabinets LLC)</label>
                                        <input type="text" className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-slate-200" value={draftShipment.consignee} onChange={e => handleDraftChange('consignee', e.target.value)} placeholder="Nhập tên Consignee..." />
                                    </div>
                                    <div>
                                        <label className="block text-slate-400 mb-1">Sales Phụ Trách (vd: Nguyễn Văn A)</label>
                                        <input type="text" className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-slate-200" value={draftShipment.sales} onChange={e => handleDraftChange('sales', e.target.value)} placeholder="Nhập tên Sales..." />
                                    </div>
                                </div>

                                <div className="space-y-2 p-2.5 bg-slate-950/60 rounded border border-slate-800">
                                    <p className="font-bold text-blue-400 text-[11px] uppercase tracking-wider">2. Tuyến Vận Tải (POL / POD)</p>
                                    <div>
                                        <label className="block text-slate-400 mb-1">Cảng Đi (POL)</label>
                                        <select className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-slate-200" value={draftShipment.pol} onChange={e => handleDraftChange('pol', e.target.value)}>
                                            {PORTS_DATABASE.map(p => <option key={p.code} value={p.code}>{p.name}</option>)}
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-slate-400 mb-1">Cảng Đến (POD)</label>
                                        <select className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-slate-200" value={draftShipment.pod} onChange={e => handleDraftChange('pod', e.target.value)}>
                                            {PORTS_DATABASE.map(p => <option key={p.code} value={p.code}>{p.name}</option>)}
                                        </select>
                                        {formErrors.pod && <p className="text-red-400 text-[10px] mt-0.5">{formErrors.pod}</p>}
                                    </div>
                                    <div>
                                        <label className="block text-slate-400 mb-1">Loại Hàng Hóa (vd: Wooden kitchen cabinets)</label>
                                        <input type="text" className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-slate-200" value={draftShipment.commodity} onChange={e => handleDraftChange('commodity', e.target.value)} placeholder="Tên hàng kèm mã HS..." />
                                    </div>
                                </div>

                                <div className="space-y-2 p-2.5 bg-slate-950/60 rounded border border-slate-800">
                                    <p className="font-bold text-blue-400 text-[11px] uppercase tracking-wider">3. Quy Mô & Container</p>
                                    <div className="grid grid-cols-2 gap-2">
                                        <div>
                                            <label className="block text-slate-400 mb-1">Loại Cont</label>
                                            <select className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-slate-200" value={draftShipment.containerType} onChange={e => handleDraftChange('containerType', e.target.value)}>
                                                {CONTAINER_TYPES.map(ct => <option key={ct} value={ct}>{ct}</option>)}
                                            </select>
                                        </div>
                                        <div>
                                            <label className="block text-slate-400 mb-1">Số Lượng</label>
                                            <input type="number" min="1" className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-slate-200" value={draftShipment.quantity} onChange={e => handleDraftChange('quantity', parseInt(e.target.value) || 0)} />
                                        </div>
                                    </div>
                                    <div>
                                        <label className="block text-slate-400 mb-1">Hãng Tàu Mong Muốn</label>
                                        <select className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-slate-200" value={draftShipment.carrier} onChange={e => handleDraftChange('carrier', e.target.value)}>
                                            {CARRIERS_LIST.map(c => <option key={c} value={c}>{c}</option>)}
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-slate-400 mb-1">Mục tiêu Biên Lãi (%)</label>
                                        <input type="number" value={targetMargin} onChange={e => setTargetMargin(parseFloat(e.target.value) || 0)} className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-slate-200" />
                                    </div>
                                </div>

                                <div className="space-y-2 p-2.5 bg-slate-950/60 rounded border border-slate-800">
                                    <p className="font-bold text-blue-400 text-[11px] uppercase tracking-wider">4. Lịch Trình (ETD / ETA)</p>
                                    <div>
                                        <label className="block text-slate-400 mb-1">Ngày Book Chỗ (yyyy-mm-dd)</label>
                                        <input type="date" className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-slate-200" value={draftShipment.bookingDate} onChange={e => handleDraftChange('bookingDate', e.target.value)} />
                                    </div>
                                    <div className="grid grid-cols-2 gap-2">
                                        <div>
                                            <label className="block text-slate-400 mb-1">ETD Thực Tế</label>
                                            <input type="date" className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-slate-200" value={draftShipment.etd} onChange={e => handleDraftChange('etd', e.target.value)} />
                                        </div>
                                        <div>
                                            <label className="block text-slate-400 mb-1">ETA Dự Kiến</label>
                                            <input type="date" className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-slate-200" value={draftShipment.eta} onChange={e => handleDraftChange('eta', e.target.value)} />
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {etaWarning && (
                                <div className="bg-red-950/80 border border-red-800 p-2 text-xs text-red-200 rounded my-2">
                                    <p className="font-bold">Cảnh báo: ETA nhỏ hơn ETD!</p>
                                    <div className="flex gap-2 mt-1">
                                        <button className="bg-slate-700 px-2 py-1 rounded text-white" onClick={() => setEtaWarning(false)}>Sửa lại</button>
                                        <button className="bg-red-700 text-white px-2 py-1 rounded" onClick={() => { setEtaWarning(false); handleApplyAndUpdate(); }}>Giữ nguyên</button>
                                    </div>
                                </div>
                            )}

                            <div className="mt-3 pt-3 border-t border-slate-800 flex flex-col gap-2">
                                <button onClick={handleApplyAndUpdate} className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded text-xs shadow transition">
                                    Hoàn thành và cập nhật dữ liệu
                                </button>
                                <button onClick={() => setDraftShipment({ ...shipmentState })} className="w-full bg-slate-800 hover:bg-slate-700 text-slate-300 py-1.5 rounded text-xs">
                                    Đặt lại thông tin nháp
                                </button>
                            </div>
                        </div>

                        <div className="flex-1 flex flex-col bg-slate-950">
                            <div className="bg-slate-900 border-b border-slate-800 flex px-6 gap-6 text-xs font-medium">
                                {[
                                    { id: "dashboard", label: "Dashboard Tổng quan" },
                                    { id: "quotation", label: "Báo giá & Lợi nhuận" },
                                    { id: "space", label: "Dự báo Space" },
                                    { id: "peak", label: "Mùa cao điểm" },
                                    { id: "slot", label: "Sàn Slot (DEMO)" }
                                ].map(tab => (
                                    <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`py-3 border-b-2 transition ${activeTab === tab.id ? 'border-blue-500 text-blue-400 font-bold' : 'border-transparent text-slate-400 hover:text-slate-200'}`}>
                                        {tab.label}
                                    </button>
                                ))}
                            </div>

                            <div className="flex-1 p-6 overflow-y-auto">
                                {activeTab === "dashboard" && (
                                    <div className="space-y-4">
                                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                            <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
                                                <p className="text-xs text-slate-400">Tuyến vận chuyển</p>
                                                <p className="text-base font-bold text-blue-400 mt-1">{shipmentState.pol} -> {shipmentState.pod}</p>
                                                <p className="text-[10px] text-slate-400 mt-1">{shipmentState.containerType} ({shipmentState.quantity} cont) - {shipmentState.commodity}</p>
                                            </div>
                                            <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
                                                <p className="text-xs text-slate-400">Báo giá khả dụng</p>
                                                <p className="text-base font-bold text-emerald-400 mt-1">{matchingQuotations.length} Hãng tàu</p>
                                                <p className="text-[10px] text-slate-400 mt-1">Sales: {shipmentState.sales}</p>
                                            </div>
                                            <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
                                                <p className="text-xs text-slate-400">Rủi ro Space</p>
                                                <p className="text-base font-bold text-amber-400 mt-1">
                                                    {matchingSpaces.length > 0 ? (calculateSpaceDeficit(shipmentState.quantity, matchingSpaces[0].availableSpace).deficit > 0 ? "Cao" : "Thấp") : "Chưa đủ dữ liệu"}
                                                </p>
                                                <p className="text-[10px] text-slate-400 mt-1">ETD: {shipmentState.etd}</p>
                                            </div>
                                            <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
                                                <p className="text-xs text-slate-400">Mục tiêu Biên Lãi</p>
                                                <p className="text-base font-bold text-blue-400 mt-1">{targetMargin}%</p>
                                                <p className="text-[10px] text-slate-400 mt-1">Khách: {shipmentState.consignee}</p>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {activeTab === "quotation" && (
                                    <div className="space-y-4">
                                        <h3 className="font-bold text-sm text-slate-200">So sánh phương án hãng tàu ({shipmentState.pol} -> {shipmentState.pod}) cho {shipmentState.commodity}</h3>
                                        {matchingQuotations.length === 0 ? (
                                            <div className="bg-amber-950/50 border border-amber-800 p-4 text-xs text-amber-200 rounded">Chưa có dữ liệu giá cước cho tuyến này.</div>
                                        ) : (
                                            <div className="bg-slate-900 border border-slate-800 rounded shadow-sm overflow-x-auto">
                                                <table className="w-full text-left text-xs">
                                                    <thead className="bg-slate-800/80 border-b border-slate-700 text-slate-300">
                                                        <tr>
                                                            <th className="p-3">Hãng tàu</th>
                                                            <th className="p-3">ETD / ETA</th>
                                                            <th className="p-3">Tổng chi phí</th>
                                                            <th className="p-3">Giá bán đề xuất ($)</th>
                                                            <th className="p-3">Biên lợi nhuận</th>
                                                            <th className="p-3">Trạng thái</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody className="divide-y divide-slate-800">
                                                        {matchingQuotations.map(q => {
                                                            const totalCost = calculateTotalCost(q, shipmentState.quantity);
                                                            const sellingPricePerUnit = sellingPrices[q.id] || 0;
                                                            const metrics = calculateProfitMetrics(totalCost, sellingPricePerUnit, shipmentState.quantity, targetMargin);
                                                            return (
                                                                <tr key={q.id} className="hover:bg-slate-800/40">
                                                                    <td className="p-3 font-bold text-slate-200">{q.carrier}</td>
                                                                    <td className="p-3 text-slate-300">{q.etd} / {q.eta}</td>
                                                                    <td className="p-3 font-semibold text-slate-200">${totalCost.toLocaleString()}</td>
                                                                    <td className="p-3">
                                                                        <input type="number" value={sellingPricePerUnit} onChange={e => setSellingPrices({...sellingPrices, [q.id]: parseFloat(e.target.value) || 0})} className="w-24 bg-slate-950 border border-slate-700 rounded p-1 text-blue-400 font-bold" />
                                                                        <p className="text-[10px] text-slate-400 mt-0.5">Tối thiểu: ${metrics.minSellingPricePerUnit.toFixed(2)}</p>
                                                                    </td>
                                                                    <td className="p-3 font-bold text-slate-200">{metrics.revenue > 0 ? `${metrics.marginPercent.toFixed(2)}%` : "-"}</td>
                                                                    <td className="p-3"><span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-800">{metrics.status}</span></td>
                                                                </tr>
                                                            );
                                                        })}
                                                    </tbody>
                                                </table>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {activeTab === "space" && (
                                    <div className="space-y-4">
                                        <h3 className="font-bold text-sm text-slate-200">Dự báo Space khả dụng</h3>
                                        {matchingSpaces.length === 0 ? (
                                            <div className="bg-amber-950/50 border border-amber-800 p-4 text-xs text-amber-200 rounded">Chưa đủ dữ liệu xác định space khả dụng.</div>
                                        ) : (
                                            <div className="bg-slate-900 border border-slate-800 p-4 rounded text-xs space-y-2">
                                                {matchingSpaces.map(sp => {
                                                    const deficitObj = calculateSpaceDeficit(shipmentState.quantity, sp.availableSpace);
                                                    return (
                                                        <div key={sp.id} className="grid grid-cols-4 gap-4 p-3 bg-slate-950 rounded border border-slate-800">
                                                            <div>Hãng tàu: <span className="font-bold text-slate-200">{sp.carrier}</span></div>
                                                            <div>Space khả dụng: <span className="font-bold text-emerald-400">{sp.availableSpace} cont</span></div>
                                                            <div>Nhu cầu: <span className="font-bold text-blue-400">{shipmentState.quantity} cont</span></div>
                                                            <div>Thiếu hụt: <span className="font-bold text-red-400">{deficitObj.deficit} cont</span></div>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        )}
                                    </div>
                                )}

                                {activeTab === "peak" && (
                                    <div className="space-y-3">
                                        <h3 className="font-bold text-sm text-slate-200">Mùa cao điểm & Booking</h3>
                                        {PEAK_EVENTS.map(ev => (
                                            <div key={ev.id} className="bg-slate-900 border border-slate-800 p-4 rounded text-xs space-y-1">
                                                <div className="flex justify-between"><span className="font-bold text-sm text-slate-200">{ev.name}</span><span className="bg-red-950 text-red-300 border border-red-800 font-bold px-2 py-0.5 rounded text-[10px]">{ev.certainty}</span></div>
                                                <p className="text-slate-400">{ev.reason}</p>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {activeTab === "slot" && (
                                    <div className="space-y-3">
                                        <h3 className="font-bold text-sm text-slate-200">Sàn Slot (DEMO)</h3>
                                        {matchingSlots.map(slot => (
                                            <div key={slot.id} className="bg-slate-900 border border-slate-800 p-4 rounded text-xs flex justify-between items-center">
                                                <div>
                                                    <p className="font-bold text-slate-200">{slot.provider} — {slot.carrier}</p>
                                                    <p className="text-slate-400">Còn lại: <span className="font-bold text-blue-400">{slot.remainingSlots} slot</span> | Giá: ${slot.sellingPrice}</p>
                                                </div>
                                                <button onClick={() => {
                                                    if (shipmentState.quantity > slot.remainingSlots) alert("Vượt số slot còn lại!");
                                                    else {
                                                        setSlots(slots.map(s => s.id === slot.id ? {...s, remainingSlots: s.remainingSlots - shipmentState.quantity} : s));
                                                        alert("Đã ghi nhận yêu cầu DEMO mua slot thành công!");
                                                    }
                                                }} className="bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1.5 rounded font-medium">Mua Slot</button>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            );
        }

        ReactDOM.createRoot(document.getElementById('root')).render(<App />);
    </script>
</body>
</html>

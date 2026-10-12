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
<body class="bg-slate-50 text-slate-800 font-sans">
    <div id="root"></div>

    <script type="text/babel">
        const { useState } = React;

        const PORTS_DATABASE = [
            { code: "VNSGN", name: "Cát Lái (Ho Chi Minh)", country: "Vietnam" },
            { code: "VNBVT", name: "Cái Mép (Ba Ria - Vung Tau)", country: "Vietnam" },
            { code: "VNHPH", name: "Hải Phòng", country: "Vietnam" },
            { code: "VNDAD", name: "Đà Nẵng", country: "Vietnam" },
            { code: "VNUIH", name: "Quy Nhơn", country: "Vietnam" },
            { code: "CNSHA", name: "Shanghai", country: "China" },
            { code: "CNNGB", name: "Ningbo", country: "China" },
            { code: "CNYAN", name: "Shenzhen / Yantian", country: "China" },
            { code: "CNTAO", name: "Qingdao", country: "China" },
            { code: "KRPUS", name: "Busan", country: "South Korea" },
            { code: "SGSIN", name: "Singapore", country: "Singapore" },
            { code: "USLAX", name: "Los Angeles", country: "United States" },
            { code: "USLGB", name: "Long Beach", country: "United States" },
            { code: "USNYC", name: "New York / New Jersey", country: "United States" },
            { code: "NLRTM", name: "Rotterdam", country: "Netherlands" },
            { code: "DEHAM", name: "Hamburg", country: "Germany" },
            { code: "BEANR", name: "Antwerp", country: "Belgium" }
        ];

        const CONTAINER_TYPES = [
            "20'GP", "40'GP", "40'HC", "45'HC", "Reefer 20'", "Reefer 40'", "Open Top", "Flat Rack"
        ];

        const INITIAL_QUOTATIONS = [
            {
                id: "QT-01", carrier: "Maersk Line", pol: "VNSGN", pod: "USLAX", containerType: "40'HC",
                etd: "2026-11-10", eta: "2026-11-28", oceanFreight: 3200, pss: 300, gri: 0, bafLss: 250,
                localCharges: 180, docFee: 50, trucking: 350, slotFee: 0, otherFees: 0,
                source: "LIVE", sourceName: "Maersk API Connect"
            },
            {
                id: "QT-02", carrier: "CMA CGM", pol: "VNSGN", pod: "USLAX", containerType: "40'HC",
                etd: "2026-11-12", eta: "2026-11-30", oceanFreight: 3100, pss: 250, gri: 100, bafLss: 220,
                localCharges: 170, docFee: 50, trucking: 350, slotFee: 0, otherFees: 0,
                source: "MANUAL", sourceName: "Local Rate Sheet Q4"
            }
        ];

        const INITIAL_SPACES = [
            {
                id: "SP-01", pol: "VNSGN", pod: "USLAX", containerType: "40'HC", carrier: "Maersk Line",
                availableSpace: 3, source: "LIVE", sourceName: "Carrier Allocation Portal"
            }
        ];

        const INITIAL_SLOTS = [
            {
                id: "SLOT-01", provider: "Global Forwarder Vina", pol: "VNSGN", pod: "USLAX", carrier: "Evergreen",
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
                shipper: "Global Vina Garment Co.",
                consignee: "US Retail Brand Inc.",
                customer: "ABC Logistics Corp",
                pol: "VNSGN",
                pod: "USLAX",
                containerType: "40'HC",
                quantity: 2,
                etd: "2026-11-10",
                eta: "2026-11-28",
                commodity: "Garments & Textiles",
                updatedAt: "2026-10-12 10:00"
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
                setSuccessNotice(`Cap nhat lo hang thanh cong luc ${nowStr}! Tat ca phan he da dong bo.`);
                setTimeout(() => setSuccessNotice(""), 5000);
            };

            const matchingQuotations = INITIAL_QUOTATIONS.filter(q => q.pol === shipmentState.pol && q.pod === shipmentState.pod && q.containerType === shipmentState.containerType);
            const matchingSpaces = INITIAL_SPACES.filter(s => s.pol === shipmentState.pol && s.pod === shipmentState.pod && s.containerType === shipmentState.containerType);
            const matchingSlots = slots.filter(sl => sl.pol === shipmentState.pol && sl.pod === shipmentState.pod && sl.containerType === shipmentState.containerType);

            return (
                <div className="min-h-screen flex flex-col">
                    <header className="bg-slate-900 text-white px-6 py-4 flex justify-between items-center shadow">
                        <div>
                            <h1 className="text-lg font-bold">LOGISPACE SIMULATOR <span className="text-xs bg-blue-600 px-2 py-0.5 rounded ml-2">Sales Forwarding Edition</span></h1>
                            <p className="text-xs text-slate-400">He thong mo phong nghiep vu Sales Forwarding, Bao gia & San Slot</p>
                        </div>
                        <div className="text-right text-xs text-slate-300">
                            <p>Trang thai: <span className="text-emerald-400 font-semibold">[Da dong bo - Confirmed]</span></p>
                            <p>Cap nhat: {shipmentState.updatedAt}</p>
                        </div>
                    </header>

                    {successNotice && (
                        <div className="bg-emerald-600 text-white px-6 py-2.5 text-xs text-center font-medium shadow">
                            {successNotice}
                        </div>
                    )}

                    <div className="flex-1 flex flex-col md:flex-row">
                        <div className="w-full md:w-80 bg-white border-r border-slate-200 p-4 flex flex-col shadow-sm">
                            <div className="flex justify-between items-center mb-3">
                                <h2 className="font-bold text-slate-800 text-sm">Thong tin Lo hang</h2>
                                <span className="text-[10px] bg-amber-100 text-amber-800 font-bold px-2 py-0.5 rounded">Nhap / Dang sua</span>
                            </div>

                            <div className="space-y-3 flex-1 text-xs">
                                <div>
                                    <label className="block font-semibold text-slate-600 mb-1">Cang di (POL)</label>
                                    <select className="w-full border rounded p-1.5 bg-slate-50" value={draftShipment.pol} onChange={e => handleDraftChange('pol', e.target.value)}>
                                        {PORTS_DATABASE.map(p => <option key={p.code} value={p.code}>{p.name} ({p.code})</option>)}
                                    </select>
                                </div>
                                <div>
                                    <label className="block font-semibold text-slate-600 mb-1">Cang den (POD)</label>
                                    <select className="w-full border rounded p-1.5 bg-slate-50" value={draftShipment.pod} onChange={e => handleDraftChange('pod', e.target.value)}>
                                        {PORTS_DATABASE.map(p => <option key={p.code} value={p.code}>{p.name} ({p.code})</option>)}
                                    </select>
                                    {formErrors.pod && <p className="text-red-500 text-[10px] mt-0.5">{formErrors.pod}</p>}
                                </div>
                                <div className="grid grid-cols-2 gap-2">
                                    <div>
                                        <label className="block font-semibold text-slate-600 mb-1">Loai Cont</label>
                                        <select className="w-full border rounded p-1.5 bg-slate-50" value={draftShipment.containerType} onChange={e => handleDraftChange('containerType', e.target.value)}>
                                            {CONTAINER_TYPES.map(ct => <option key={ct} value={ct}>{ct}</option>)}
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block font-semibold text-slate-600 mb-1">So luong</label>
                                        <input type="number" min="1" className="w-full border rounded p-1.5" value={draftShipment.quantity} onChange={e => handleDraftChange('quantity', parseInt(e.target.value) || 0)} />
                                    </div>
                                </div>
                                <div className="grid grid-cols-2 gap-2">
                                    <div>
                                        <label className="block font-semibold text-slate-600 mb-1">ETD</label>
                                        <input type="date" className="w-full border rounded p-1.5" value={draftShipment.etd} onChange={e => handleDraftChange('etd', e.target.value)} />
                                    </div>
                                    <div>
                                        <label className="block font-semibold text-slate-600 mb-1">ETA</label>
                                        <input type="date" className="w-full border rounded p-1.5" value={draftShipment.eta} onChange={e => handleDraftChange('eta', e.target.value)} />
                                    </div>
                                </div>
                                <div>
                                    <label className="block font-semibold text-slate-600 mb-1">Nhom hang</label>
                                    <input type="text" className="w-full border rounded p-1.5" value={draftShipment.commodity} onChange={e => handleDraftChange('commodity', e.target.value)} />
                                </div>
                            </div>

                            {etaWarning && (
                                <div className="bg-red-50 border border-red-200 p-2 text-xs text-red-700 rounded my-2">
                                    <p className="font-bold">ETA nho hon ETD!</p>
                                    <div className="flex gap-2 mt-1">
                                        <button className="bg-slate-200 px-2 py-1 rounded" onClick={() => setEtaWarning(false)}>Sua lai</button>
                                        <button className="bg-red-600 text-white px-2 py-1 rounded" onClick={() => { setEtaWarning(false); handleApplyAndUpdate(); }}>Giu nguyen</button>
                                    </div>
                                </div>
                            )}

                            <div className="mt-3 pt-3 border-t border-slate-200 flex flex-col gap-2">
                                <button onClick={handleApplyAndUpdate} className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded text-xs shadow transition">
                                    Hoan thanh va cap nhat du lieu
                                </button>
                                <button onClick={() => setDraftShipment({ ...shipmentState })} className="w-full bg-slate-100 hover:bg-slate-200 text-slate-700 py-1 rounded text-xs">
                                    Dat lai
                                </button>
                            </div>
                        </div>

                        <div className="flex-1 flex flex-col">
                            <div className="bg-white border-b border-slate-200 flex px-6 gap-6 text-xs font-medium">
                                {[
                                    { id: "dashboard", label: "Dashboard" },
                                    { id: "quotation", label: "Bao gia & Loi nhuan" },
                                    { id: "space", label: "Du bao Space" },
                                    { id: "peak", label: "Mua cao diem" },
                                    { id: "slot", label: "San Slot (DEMO)" }
                                ].map(tab => (
                                    <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`py-3 border-b-2 transition ${activeTab === tab.id ? 'border-blue-600 text-blue-600 font-bold' : 'border-transparent text-slate-500 hover:text-slate-800'}`}>
                                        {tab.label}
                                    </button>
                                ))}
                            </div>

                            <div className="flex-1 p-6 overflow-y-auto">
                                {activeTab === "dashboard" && (
                                    <div className="space-y-4">
                                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                            <div className="bg-white p-4 rounded border border-slate-200">
                                                <p className="text-xs text-slate-500">Tuyen van chuyen</p>
                                                <p className="text-base font-bold text-blue-600 mt-1">{shipmentState.pol} -> {shipmentState.pod}</p>
                                                <p className="text-[10px] text-slate-400 mt-1">{shipmentState.containerType} ({shipmentState.quantity} cont)</p>
                                            </div>
                                            <div className="bg-white p-4 rounded border border-slate-200">
                                                <p className="text-xs text-slate-500">Bao gia kha dung</p>
                                                <p className="text-base font-bold text-emerald-600 mt-1">{matchingQuotations.length} Hang tau</p>
                                            </div>
                                            <div className="bg-white p-4 rounded border border-slate-200">
                                                <p className="text-xs text-slate-500">Rui ro Space</p>
                                                <p className="text-base font-bold text-amber-600 mt-1">
                                                    {matchingSpaces.length > 0 ? (calculateSpaceDeficit(shipmentState.quantity, matchingSpaces[0].availableSpace).deficit > 0 ? "Cao" : "Thap") : "Chua du du lieu"}
                                                </p>
                                            </div>
                                            <div className="bg-white p-4 rounded border border-slate-200">
                                                <p className="text-xs text-slate-500">Bien loi nhuan muc tieu</p>
                                                <div className="flex items-center gap-1 mt-1">
                                                    <input type="number" value={targetMargin} onChange={e => setTargetMargin(parseFloat(e.target.value) || 0)} className="w-14 border rounded px-1.5 py-0.5 text-sm font-bold text-blue-600" />
                                                    <span className="text-sm font-bold">%</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {activeTab === "quotation" && (
                                    <div className="space-y-4">
                                        <h3 className="font-bold text-sm text-slate-800">So sanh phuong an hang tau ({shipmentState.pol} -> {shipmentState.pod})</h3>
                                        {matchingQuotations.length === 0 ? (
                                            <div className="bg-amber-50 border border-amber-200 p-4 text-xs text-amber-800 rounded">Chua co du lieu gia cuoc cho tuyen nay.</div>
                                        ) : (
                                            <div className="bg-white border border-slate-200 rounded shadow-sm overflow-x-auto">
                                                <table className="w-full text-left text-xs">
                                                    <thead className="bg-slate-100 border-b border-slate-200 text-slate-700">
                                                        <tr>
                                                            <th className="p-3">Hang tau</th>
                                                            <th className="p-3">ETD / ETA</th>
                                                            <th className="p-3">Tong chi phi</th>
                                                            <th className="p-3">Gia ban de xuat ($)</th>
                                                            <th className="p-3">Bien loi nhuan</th>
                                                            <th className="p-3">Trang thai</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody className="divide-y divide-slate-100">
                                                        {matchingQuotations.map(q => {
                                                            const totalCost = calculateTotalCost(q, shipmentState.quantity);
                                                            const sellingPricePerUnit = sellingPrices[q.id] || 0;
                                                            const metrics = calculateProfitMetrics(totalCost, sellingPricePerUnit, shipmentState.quantity, targetMargin);
                                                            return (
                                                                <tr key={q.id}>
                                                                    <td className="p-3 font-bold">{q.carrier}</td>
                                                                    <td className="p-3">{q.etd} / {q.eta}</td>
                                                                    <td className="p-3 font-semibold">${totalCost.toLocaleString()}</td>
                                                                    <td className="p-3">
                                                                        <input type="number" value={sellingPricePerUnit} onChange={e => setSellingPrices({...sellingPrices, [q.id]: parseFloat(e.target.value) || 0})} className="w-24 border rounded p-1 text-blue-600 font-bold" />
                                                                        <p className="text-[10px] text-slate-400">Toi thieu: ${metrics.minSellingPricePerUnit.toFixed(2)}</p>
                                                                    </td>
                                                                    <td className="p-3 font-bold">{metrics.revenue > 0 ? `${metrics.marginPercent.toFixed(2)}%` : "-"}</td>
                                                                    <td className="p-3"><span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">{metrics.status}</span></td>
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
                                        <h3 className="font-bold text-sm text-slate-800">Du bao Space kha dung</h3>
                                        {matchingSpaces.length === 0 ? (
                                            <div className="bg-amber-50 border border-amber-200 p-4 text-xs text-amber-800 rounded">Chua du du lieu xac dinh space kha dung.</div>
                                        ) : (
                                            <div className="bg-white border border-slate-200 p-4 rounded text-xs space-y-2">
                                                {matchingSpaces.map(sp => {
                                                    const deficitObj = calculateSpaceDeficit(shipmentState.quantity, sp.availableSpace);
                                                    return (
                                                        <div key={sp.id} className="grid grid-cols-4 gap-4 p-3 bg-slate-50 rounded">
                                                            <div>Hang tau: <span className="font-bold">{sp.carrier}</span></div>
                                                            <div>Space kha dung: <span className="font-bold text-emerald-600">{sp.availableSpace} cont</span></div>
                                                            <div>Nhu cau: <span className="font-bold text-blue-600">{shipmentState.quantity} cont</span></div>
                                                            <div>Thieu hut: <span className="font-bold text-red-600">{deficitObj.deficit} cont</span></div>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        )}
                                    </div>
                                )}

                                {activeTab === "peak" && (
                                    <div className="space-y-3">
                                        <h3 className="font-bold text-sm text-slate-800">Mua cao diem & Booking</h3>
                                        {PEAK_EVENTS.map(ev => (
                                            <div key={ev.id} className="bg-white border border-slate-200 p-4 rounded text-xs space-y-1">
                                                <div className="flex justify-between"><span className="font-bold text-sm">{ev.name}</span><span className="bg-red-100 text-red-800 font-bold px-2 py-0.5 rounded text-[10px]">{ev.certainty}</span></div>
                                                <p className="text-slate-600">{ev.reason}</p>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {activeTab === "slot" && (
                                    <div className="space-y-3">
                                        <h3 className="font-bold text-sm text-slate-800">San Slot (DEMO)</h3>
                                        {matchingSlots.map(slot => (
                                            <div key={slot.id} className="bg-white border border-slate-200 p-4 rounded text-xs flex justify-between items-center">
                                                <div>
                                                    <p className="font-bold">{slot.provider} — {slot.carrier}</p>
                                                    <p className="text-slate-500">Con lai: <span className="font-bold text-blue-600">{slot.remainingSlots} slot</span> | Gia: ${slot.sellingPrice}</p>
                                                </div>
                                                <button onClick={() => {
                                                    if (shipmentState.quantity > slot.remainingSlots) alert("Vuot so slot con lai!");
                                                    else {
                                                        setSlots(slots.map(s => s.id === slot.id ? {...s, remainingSlots: s.remainingSlots - shipmentState.quantity} : s));
                                                        alert("Da ghi nhan yeu cau DEMO mua slot thanh cong!");
                                                    }
                                                }} className="bg-emerald-600 text-white px-3 py-1.5 rounded font-medium">Mua Slot</button>
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

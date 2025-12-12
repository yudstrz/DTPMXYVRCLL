"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, ArrowRight, Check, Loader2, Award } from "lucide-react";
import { motion } from "framer-motion";

interface Occupation {
    id: string;
    nama: string;
    score: number;
    gap: string;
}

export default function ResultsPage() {
    const router = useRouter();
    const [loading, setLoading] = useState(true);
    const [occupations, setOccupations] = useState<Occupation[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [selectedId, setSelectedId] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            const profileStr = localStorage.getItem("userProfile");
            if (!profileStr) {
                router.push("/");
                return;
            }

            const profile = JSON.parse(profileStr);
            try {
                const res = await fetch("/api/match-profile", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text: profile.cvText, top_k: 3 }),
                });
                const json = await res.json();
                if (json.error) {
                    setError(json.error);
                } else if (json.recommendations) {
                    setOccupations(json.recommendations);
                }
            } catch (err) {
                console.error("Error matching", err);
                setError("Terjadi kesalahan koneksi. Silakan coba lagi.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [router]);

    const handleSelect = (occ: Occupation) => {
        setSelectedId(occ.id);
        localStorage.setItem("selectedOccupation", JSON.stringify(occ));
        setTimeout(() => {
            router.push(`/career`);
        }, 500);
    };

    return (
        <div className="min-h-screen bg-[#0f1117] text-white p-6 md:p-12">
            <div className="max-w-6xl mx-auto">
                <button
                    onClick={() => router.push("/")}
                    className="flex items-center text-gray-400 hover:text-white mb-8 transition-colors"
                >
                    <ArrowLeft className="w-5 h-5 mr-2" />
                    Kembali ke Upload
                </button>

                <h1 className="text-3xl md:text-5xl font-bold mb-2">Rekomendasi Karir</h1>
                <p className="text-gray-400 mb-12">Berdasarkan analisis skill dan pengalaman Anda (SKKNI Match)</p>

                {loading ? (
                    <div className="flex flex-col items-center justify-center py-20 space-y-4">
                        <Loader2 className="w-12 h-12 text-orange-500 animate-spin" />
                        <p className="text-gray-400 animate-pulse">Memproses kecocokan profil...</p>
                    </div>
                ) : error ? (
                    <div className="text-center py-20">
                        <div className="bg-red-500/10 border border-red-500/50 rounded-2xl p-6 max-w-2xl mx-auto">
                            <h3 className="text-xl font-bold text-red-500 mb-2">Terjadi Kesalahan</h3>
                            <p className="text-gray-300">{error}</p>
                            <button
                                onClick={() => window.location.reload()}
                                className="mt-4 px-6 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-white font-medium transition-colors"
                            >
                                Coba Lagi
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="grid md:grid-cols-3 gap-6">
                        {occupations.map((occ, idx) => (
                            <motion.div
                                key={occ.id}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: idx * 0.1 }}
                                className={`
                    relative p-8 rounded-3xl border transition-all cursor-pointer group flex flex-col justify-between
                    ${selectedId === occ.id
                                        ? 'bg-[#1c1f2b] border-orange-500 shadow-[0_0_30px_rgba(249,115,22,0.3)]'
                                        : 'bg-[#1c1f2b] border-gray-800 hover:border-orange-500/50 hover:shadow-xl'
                                    }
                `}
                                onClick={() => handleSelect(occ)}
                            >
                                <div>
                                    <div className="flex justify-between items-start mb-6">
                                        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-orange-500/20 to-yellow-500/10 flex items-center justify-center text-orange-400">
                                            <Award className="w-6 h-6" />
                                        </div>
                                        <div className="px-3 py-1 rounded-full bg-green-900/30 border border-green-800 text-green-400 text-xs font-bold">
                                            {(occ.score * 100).toFixed(0)}% Match
                                        </div>
                                    </div>

                                    <h3 className="text-xl font-bold mb-2 group-hover:text-orange-400 transition-colors">{occ.nama}</h3>
                                    <p className="text-sm text-gray-500 mb-4 font-mono">ID: {occ.id}</p>
                                    <div className="text-xs text-gray-400">
                                        <span className="block mb-1 font-semibold text-gray-300">Skill Gap:</span>
                                        {occ.gap || "Analisis gap belum tersedia"}
                                    </div>
                                </div>

                                <div className="mt-8">
                                    <button className={`w-full py-3 rounded-xl font-semibold flex items-center justify-center transition-all ${selectedId === occ.id
                                        ? 'bg-orange-600 text-white'
                                        : 'bg-gray-800 text-gray-300 group-hover:bg-gray-700'
                                        }`}>
                                        {selectedId === occ.id ? (
                                            <>Terpilih <Check className="w-4 h-4 ml-2" /></>
                                        ) : (
                                            <>Pilih Karir Ini <ArrowRight className="w-4 h-4 ml-2 opacity-0 group-hover:opacity-100 transition-opacity" /></>
                                        )}
                                    </button>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

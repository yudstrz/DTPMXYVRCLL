"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, ArrowRight, Check, Loader2, Award, BookOpen, Briefcase, Copy, ExternalLink, Search } from "lucide-react";
import { motion } from "framer-motion";

interface Occupation {
    id: string;
    nama: string;
    score: number;
    gap: string;
}

interface Course {
    title: string;
    provider: string;
    level: string;
    duration: string;
    image: string;
    url: string;
}

const RSS_JOBS = [
    {
        title: "Junior Python Developer",
        company: "Tech Corp Indonesia",
        location: "Remote",
        posted: "2 hari yang lalu",
        source: "LinkedIn RSS"
    },
    {
        title: "AI Engineer Intern",
        company: "Startup AI",
        location: "Jakarta",
        posted: "5 jam yang lalu",
        source: "JobStreet RSS"
    },
    {
        title: "Data Analyst",
        company: "E-Commerce Unicorn",
        location: "Bandung",
        posted: "1 hari yang lalu",
        source: "TechInAsia RSS"
    }
];

export default function ResultsPage() {
    const router = useRouter();
    const [loading, setLoading] = useState(true);
    const [occupations, setOccupations] = useState<Occupation[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [selectedOccupationName, setSelectedOccupationName] = useState<string>("");

    // Data States
    const [courses, setCourses] = useState<Course[]>([]);

    // Fetch Data
    useEffect(() => {
        const fetchData = async () => {
            const profileStr = localStorage.getItem("userProfile");
            if (!profileStr) {
                router.push("/");
                return;
            }

            const profile = JSON.parse(profileStr);
            try {
                // 1. Get Recommendations
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
                    // Default select first one
                    if (json.recommendations.length > 0) {
                        setSelectedId(json.recommendations[0].id);
                        setSelectedOccupationName(json.recommendations[0].nama);
                    }
                }

                // 2. Get Courses
                const coursesRes = await fetch("/api/courses");
                const coursesJson = await coursesRes.json();
                if (Array.isArray(coursesJson)) {
                    setCourses(coursesJson.slice(0, 6)); // Take top 6
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
        setSelectedOccupationName(occ.nama);
    };

    // Boolean Search Logic
    const generateBooleanSearch = (site: string) => {
        const baseQuery = `"${selectedOccupationName}" AND ("Junior" OR "Associate" OR "Entry Level")`;
        switch (site) {
            case 'linkedin':
                return `https://www.linkedin.com/jobs/search/?keywords=${encodeURIComponent(baseQuery)}`;
            case 'glints':
                return `https://glints.com/id/opportunities/jobs/explore?keyword=${encodeURIComponent(selectedOccupationName)}`;
            case 'jobstreet':
                return `https://www.jobstreet.co.id/id/job-search/${encodeURIComponent(selectedOccupationName.replace(/\s+/g, '-'))}-jobs/`;
            case 'kalibrr':
                return `https://www.kalibrr.com/job-board/te/matches?text=${encodeURIComponent(selectedOccupationName)}`;
            default:
                return '#';
        }
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        alert("Query copied!");
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
                    <div className="space-y-20">
                        {/* 1. Career Recommendations */}
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

                                    <div className="mt-6 flex items-center text-orange-500 text-sm font-semibold">
                                        {selectedId === occ.id && <><Check className="w-4 h-4 mr-2" /> Selected for Search</>}
                                    </div>
                                </motion.div>
                            ))}
                        </div>

                        {/* 2. Boolean Search Generator */}
                        {selectedOccupationName && (
                            <div className="bg-[#1c1f2b] border border-gray-800 rounded-3xl p-8">
                                <div className="flex items-center space-x-4 mb-8">
                                    <div className="w-12 h-12 rounded-2xl bg-purple-500/20 flex items-center justify-center text-purple-400">
                                        <Search className="w-6 h-6" />
                                    </div>
                                    <div>
                                        <h2 className="text-2xl font-bold">Cari Lowongan "{selectedOccupationName}"</h2>
                                        <p className="text-gray-400">Gunakan Boolean Search Generator untuk hasil pencarian yang lebih akurat</p>
                                    </div>
                                </div>

                                <div className="grid md:grid-cols-2 gap-4">
                                    {['linkedin', 'glints', 'jobstreet', 'kalibrr'].map((site) => (
                                        <div key={site} className="p-4 bg-black/20 rounded-xl border border-gray-800 flex justify-between items-center group hover:bg-white/5 transition-colors">
                                            <div>
                                                <div className="text-sm text-gray-500 font-bold uppercase mb-1">{site}</div>
                                                <div className="text-gray-300 text-sm flex items-center">
                                                    Query otomatis untuk {selectedOccupationName}
                                                </div>
                                            </div>
                                            <div className="flex space-x-2">
                                                <button
                                                    onClick={() => copyToClipboard(`"${selectedOccupationName}"`)}
                                                    className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-gray-400 hover:text-white transition-colors"
                                                    title="Copy Query"
                                                >
                                                    <Copy className="w-4 h-4" />
                                                </button>
                                                <a
                                                    href={generateBooleanSearch(site)}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="p-2 bg-orange-600 hover:bg-orange-700 rounded-lg text-white transition-colors"
                                                    title="Open Search"
                                                >
                                                    <ExternalLink className="w-4 h-4" />
                                                </a>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* 3. Maxy Courses (Real Data) */}
                        <div>
                            <div className="flex items-center space-x-4 mb-8">
                                <div className="w-12 h-12 rounded-2xl bg-blue-500/20 flex items-center justify-center text-blue-400">
                                    <BookOpen className="w-6 h-6" />
                                </div>
                                <div>
                                    <h2 className="text-3xl font-bold">Rekomendasi Pelatihan</h2>
                                    <p className="text-gray-400">Tingkatkan skill Anda dengan kursus resmi dari Maxy Academy</p>
                                </div>
                            </div>

                            <div className="grid md:grid-cols-3 gap-6">
                                {courses.length > 0 ? courses.map((course, idx) => (
                                    <a href={course.url} target="_blank" key={idx} className="group bg-[#1c1f2b] border border-gray-800 rounded-2xl overflow-hidden hover:border-blue-500/50 transition-all cursor-pointer block">
                                        <div className="h-40 bg-gray-800 relative overflow-hidden">
                                            <div className="absolute inset-0 bg-gradient-to-t from-[#1c1f2b] to-transparent opacity-60" />
                                            <img src={course.image} alt={course.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                                        </div>
                                        <div className="p-6">
                                            <div className="text-xs font-bold text-orange-400 mb-2">{course.provider}</div>
                                            <h3 className="text-lg font-bold mb-2 group-hover:text-blue-400 transition-colors line-clamp-2">{course.title}</h3>
                                            <div className="flex items-center text-sm text-gray-500 space-x-4">
                                                <span>{course.level}</span>
                                                <span className="w-1 h-1 bg-gray-600 rounded-full" />
                                                <span>{course.duration}</span>
                                            </div>
                                        </div>
                                    </a>
                                )) : (
                                    <div className="col-span-3 text-center py-10 text-gray-500">
                                        Memuat data kursus...
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* 4. RSS Jobs */}
                        <div>
                            <div className="flex items-center space-x-4 mb-8">
                                <div className="w-12 h-12 rounded-2xl bg-green-500/20 flex items-center justify-center text-green-400">
                                    <Briefcase className="w-6 h-6" />
                                </div>
                                <div>
                                    <h2 className="text-3xl font-bold">Lowongan Pekerjaan Terbaru</h2>
                                    <p className="text-gray-400">Info lowongan terkini dari RSS Feed (Remote & Indonesia)</p>
                                </div>
                            </div>

                            <div className="bg-[#1c1f2b] border border-gray-800 rounded-3xl p-6 md:p-8">
                                <div className="grid gap-4">
                                    {RSS_JOBS.map((job, idx) => (
                                        <div key={idx} className="flex flex-col md:flex-row md:items-center justify-between p-4 rounded-xl hover:bg-white/5 transition-colors border border-transparent hover:border-gray-700 cursor-pointer group">
                                            <div>
                                                <h3 className="text-lg font-bold group-hover:text-green-400 transition-colors">{job.title}</h3>
                                                <div className="flex items-center text-sm text-gray-400 space-x-3 mt-1">
                                                    <span>{job.company}</span>
                                                    <span className="w-1 h-1 bg-gray-600 rounded-full" />
                                                    <span>{job.location}</span>
                                                    <span className="w-1 h-1 bg-gray-600 rounded-full" />
                                                    <span className="text-gray-500">{job.posted}</span>
                                                </div>
                                            </div>
                                            <div className="mt-4 md:mt-0 flex items-center">
                                                <span className="text-xs bg-gray-800 text-gray-400 px-3 py-1 rounded-full border border-gray-700">{job.source}</span>
                                                <ArrowRight className="w-4 h-4 ml-4 text-gray-500 group-hover:text-white transform group-hover:translate-x-1 transition-all" />
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

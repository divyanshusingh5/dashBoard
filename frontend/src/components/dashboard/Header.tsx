import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { FileSpreadsheet, Menu } from "lucide-react";

interface HeaderProps {
  onMenuClick: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  return (
    <header className="sticky top-0 z-40 bg-white border-b border-gray-200 shadow-sm">
      <div className="px-4 lg:px-6 py-3">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-3 lg:gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={onMenuClick}
              className="lg:hidden hover:bg-purple-50"
            >
              <Menu className="h-5 w-5 text-purple-700" />
            </Button>

            {/* Mitchell Logo Icon */}
            <img
              src="/mitchell-logo.svg"
              alt="Mitchell"
              className="h-10 lg:h-12 w-10 lg:w-12"
            />

            <div className="hidden sm:block w-px h-10 bg-gray-300"></div>

            <div>
              <h1 className="text-xl lg:text-2xl font-bold bg-gradient-to-r from-purple-700 via-purple-600 to-fuchsia-600 bg-clip-text text-transparent">
                ClaimIQ Analytics
              </h1>
              <p className="text-gray-600 text-xs lg:text-sm mt-0.5">
                Consensus-Driven Claims Intelligence Platform
              </p>
            </div>
          </div>

          <Link to="/extend-csv">
            <Button
              variant="outline"
              size="sm"
              className="gap-2 border-purple-300 text-purple-700 hover:bg-purple-50 hover:border-purple-400"
            >
              <FileSpreadsheet className="h-4 w-4" />
              <span className="hidden sm:inline">Extend CSV</span>
            </Button>
          </Link>
        </div>
      </div>
    </header>
  );
}

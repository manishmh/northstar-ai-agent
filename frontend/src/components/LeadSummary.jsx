import { User, Calendar, MapPin, Target, DollarSign, Home } from 'lucide-react';

const SummaryItem = ({ icon: Icon, label, value }) => {
  if (value === null || value === undefined || value === "") return null;
  
  return (
    <div className="flex items-start gap-3 py-2 border-b border-gray-100 last:border-0">
      <div className="mt-0.5 text-gray-400">
        <Icon size={16} />
      </div>
      <div>
        <div className="text-xs font-medium text-gray-500 uppercase tracking-wider">{label}</div>
        <div className="text-sm text-gray-900 font-medium capitalize mt-0.5">
          {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : String(value).replace(/_/g, ' ')}
        </div>
      </div>
    </div>
  );
};

const LeadSummary = ({ data }) => {
  if (!data || !data.lead_state) return null;
  const ls = data.lead_state;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
        <h2 className="text-sm font-semibold text-gray-800">Lead Insights</h2>
      </div>
      <div className="p-4 space-y-1">
        <SummaryItem icon={Home} label="Configuration" value={ls.configuration} />
        <SummaryItem icon={DollarSign} label="Budget" value={ls.budget} />
        <SummaryItem icon={Target} label="Purpose" value={ls.purpose} />
        <SummaryItem icon={Calendar} label="Timeline" value={ls.purchase_timeline} />
        <SummaryItem icon={User} label="Interest" value={ls.interest_level} />
        <SummaryItem icon={MapPin} label="Site Visit" value={ls.site_visit_status} />
        
        {ls.booking_reference && (
          <div className="mt-4 p-3 bg-blue-50 border border-blue-100 rounded-lg">
            <div className="text-xs font-semibold text-blue-600 uppercase tracking-wider mb-1">Booking Ref</div>
            <div className="text-sm font-mono text-blue-900">{ls.booking_reference}</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LeadSummary;
